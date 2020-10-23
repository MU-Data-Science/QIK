import numpy as np
import pickle
import argparse
from pycocotools.coco import COCO
from prettytable import PrettyTable

# Global variables
coco = None
image_list = []
captions_lst = []
image_subset = []
ground_truth_dict = None
pre_computed_results = None
category_combination = None

# Local constants
SIMILARITY_THRESHOLD = .70
IMAGE_SET_PATH = "data/15K_Dataset.pkl"
PRE_COMPUTED_RESULTS_PATH = "pre_constructed_data/15K_Results.pkl"
OUTPUT_FILE = "data/QIK_Output_Combined.txt"
DATA_DIR = 'data'
DATA_TYPE = '2017'
ANN_FILE = '{}/instances_{}.json'.format(DATA_DIR,DATA_TYPE)
CAPTIONS_FILE = '{}/captions_{}.json'.format(DATA_DIR,DATA_TYPE)
PRE_COMPUTED_GROUND_TRUTH_PATH = "pre_constructed_data/15K_Results.pkl"

def init():
    global coco, image_subset, pre_computed_results, ground_truth_dict

    # Loading annotations and creating an Index
    coco = COCO(ANN_FILE)

    # Loading the subset of images.
    image_subset = pickle.load(open(IMAGE_SET_PATH, "rb"))

    # Loading the precomputed ground truth.
    ground_truth_dict = pickle.load(open(PRE_COMPUTED_GROUND_TRUTH_PATH, "rb"))

    # Loading the precomputed results.
    pre_computed_results = pickle.load(open(PRE_COMPUTED_RESULTS_PATH, "rb"))

def evaluate(query_lst):
    print("evaluate.py :: evaluate :: Starting the evaluation!")
    print("evaluate.py :: evaluate :: Query Images Length :: ", len(query_lst))
    print("evaluate.py :: evaluate :: Query Images", query_lst)

    # length of query images
    query_lst_len = len(query_lst)

    # 1) QIK Results List.
    qik_time_lst = []
    qik_2_relevance_lst = []
    qik_4_relevance_lst = []
    qik_8_relevance_lst = []
    qik_16_relevance_lst = []

    # 2) QIK Objects 0.9 Results List.
    qik_objects_9_time_lst = []
    qik_objects_9_2_relevance_lst = []
    qik_objects_9_4_relevance_lst = []
    qik_objects_9_8_relevance_lst = []
    qik_objects_9_16_relevance_lst = []

    # 3) QIK Objects 0.8 Results List.
    qik_objects_8_time_lst = []
    qik_objects_8_2_relevance_lst = []
    qik_objects_8_4_relevance_lst = []
    qik_objects_8_8_relevance_lst = []
    qik_objects_8_16_relevance_lst = []

    for query_image in query_lst:
        print("evaluate.py :: evaluate :: Evaluation for the category combination :: %s :: with the image file :: %s" % (category_combination, query_image))

        if query_image not in pre_computed_results:
            print("evaluate.py :: evaluate ::  Skipping evaluation for :: ", query_image)
            query_lst_len -= 1
            continue

        # Defining the ground truth.
        if query_image not in ground_truth_dict:
            print("evaluate.py :: evaluate ::  Skipping evaluation for :: ", query_image, " :: since there is no ground truth available.")
            query_lst_len -= 1
            continue

        ground_truth = ground_truth_dict[query_image]
        print("evaluate.py :: evaluate :: query_image :: ", query_image)
        print("evaluate.py :: evaluate :: ground_truth :: ", ground_truth)

        # Get QIK results
        qik_results = pre_computed_results[query_image]["qik_results"]
        print("evaluate.py :: evaluate :: qik_results", qik_results)
        qik_time_lst.append(pre_computed_results[query_image]["qik_time"])

        # QIK Objects 0.9 Results List.
        qik_objects_9_results = pre_computed_results[query_image]["qik_obj_9_results"]
        print("evaluate.py :: evaluate :: qik_objects_9_results", qik_objects_9_results)
        qik_objects_9_time_lst.append(pre_computed_results[query_image]["qik_obj_9_time"])

        # QIK Objects 0.8 Results List.
        qik_objects_8_results = pre_computed_results[query_image]["qik_obj_8_results"]
        print("evaluate.py :: evaluate :: qik_objects_8_results", qik_objects_8_results)
        qik_objects_8_time_lst.append(pre_computed_results[query_image]["qik_obj_8_time"])

        # Computing the mAP values.
        if len(qik_results) <= 0 or len(qik_objects_9_results) <= 0 or len(qik_objects_8_results) <= 0:
            print("evaluate.py :: evaluate :: Skipping the query image as no results are returned :: ", query_image)
            # Decrementing the count from the list of images.
            query_lst_len -= 1
            continue

        # k = 2
        qik_2_relevance_lst.append(get_binary_relevance(qik_results[:2], ground_truth))
        qik_objects_9_2_relevance_lst.append(get_binary_relevance(qik_objects_9_results[:2], ground_truth))
        qik_objects_8_2_relevance_lst.append(get_binary_relevance(qik_objects_8_results[:2], ground_truth))

        # k=4
        qik_4_relevance_lst.append(get_binary_relevance(qik_results[:4], ground_truth))
        qik_objects_9_4_relevance_lst.append(get_binary_relevance(qik_objects_9_results[:4], ground_truth))
        qik_objects_8_4_relevance_lst.append(get_binary_relevance(qik_objects_8_results[:4], ground_truth))

        # k=8
        qik_8_relevance_lst.append(get_binary_relevance(qik_results[:8], ground_truth))
        qik_objects_9_8_relevance_lst.append(get_binary_relevance(qik_objects_9_results[:8], ground_truth))
        qik_objects_8_8_relevance_lst.append(get_binary_relevance(qik_objects_8_results[:8], ground_truth))

        # k=16
        qik_16_relevance_lst.append(get_binary_relevance(qik_results[:16], ground_truth))
        qik_objects_9_16_relevance_lst.append(get_binary_relevance(qik_objects_9_results[:16], ground_truth))
        qik_objects_8_16_relevance_lst.append(get_binary_relevance(qik_objects_8_results[:16], ground_truth))

    # Computing the mean.
    print("evaluate.py :: evaluate :: Computing the mean average precision.")

    # 1) QIK
    # k=2
    qik_2_map = get_mAP(qik_2_relevance_lst)
    print("evaluate.py :: evaluate :: QIK :: k=2 :: Mean Average Precision :: %s :: %f" % (category_combination, qik_2_map))

    # k=4
    qik_4_map = get_mAP(qik_4_relevance_lst)
    print("evaluate.py :: evaluate :: QIK :: k=4 :: Mean Average Precision :: %s :: %f" % (category_combination, qik_4_map))

    # k=8
    qik_8_map = get_mAP(qik_8_relevance_lst)
    print("evaluate.py :: evaluate :: QIK :: k=8 :: Mean Average Precision :: %s :: %f" % (category_combination, qik_8_map))

    # k=16
    qik_16_map = get_mAP(qik_16_relevance_lst)
    print("evaluate.py :: evaluate :: QIK :: k=16 :: Mean Average Precision :: %s :: %f" % (category_combination, qik_16_map))

    qik_time_avg = get_average(qik_time_lst)
    print("evaluate.py :: evaluate :: QIK :: Average time :: %f " % (qik_time_avg))

    # 2) QIK Objects 0.9 Results List.
    # k=2
    qik_objects_9_2_map = get_mAP(qik_objects_9_2_relevance_lst)
    print("evaluate.py :: evaluate :: QIK Objects 0.9 :: k=2 :: Mean Average Precision :: %s :: %f" % (category_combination, qik_objects_9_2_map))

    # k=4
    qik_objects_9_4_map = get_mAP(qik_objects_9_4_relevance_lst)
    print("evaluate.py :: evaluate :: QIK Objects 0.9 :: k=4 :: Mean Average Precision :: %s :: %f" % (category_combination, qik_objects_9_4_map))

    # k=8
    qik_objects_9_8_map = get_mAP(qik_objects_9_8_relevance_lst)
    print("evaluate.py :: evaluate :: QIK Objects 0.9 :: k=8 :: Mean Average Precision :: %s :: %f" % (category_combination, qik_objects_9_8_map))

    # k=16
    qik_objects_9_16_map = get_mAP(qik_objects_9_16_relevance_lst)
    print("evaluate.py :: evaluate :: QIK Objects 0.9 :: k=16 :: Mean Average Precision :: %s :: %f" % (category_combination, qik_objects_9_16_map))

    qik_objects_9_time_avg = get_average(qik_objects_9_time_lst)
    print("evaluate.py :: evaluate :: QIK Objects 0.9 :: Average time :: %f " % (qik_objects_9_time_avg))

    # 3) QIK Objects 0.8 Results List.
    # k=2
    qik_objects_8_2_map = get_mAP(qik_objects_8_2_relevance_lst)
    print("evaluate.py :: evaluate :: QIK Objects 0.8 :: k=2 :: Mean Average Precision :: %s :: %f" % (category_combination, qik_objects_8_2_map))

    # k=4
    qik_objects_8_4_map = get_mAP(qik_objects_8_4_relevance_lst)
    print("evaluate.py :: evaluate :: QIK Objects 0.8 :: k=4 :: Mean Average Precision :: %s :: %f" % (category_combination, qik_objects_8_4_map))

    # k=8
    qik_objects_8_8_map = get_mAP(qik_objects_8_8_relevance_lst)
    print("evaluate.py :: evaluate :: QIK Objects 0.8 :: k=8 :: Mean Average Precision :: %s :: %f" % (category_combination, qik_objects_8_8_map))

    # k=16
    qik_objects_8_16_map = get_mAP(qik_objects_8_16_relevance_lst)
    print("evaluate.py :: evaluate :: QIK Objects 0.8 :: k=16 :: Mean Average Precision :: %s :: %f" % (category_combination, qik_objects_8_16_map))

    qik_objects_8_time_avg = get_average(qik_objects_8_time_lst)
    print("evaluate.py :: evaluate :: QIK Objects 0.8 :: Average time :: %f " % (qik_objects_8_time_avg))

    # Getting the print string
    output_str = category_combination, qik_2_map, qik_4_map, qik_8_map, qik_16_map, \
                 qik_objects_9_2_map, qik_objects_9_4_map, qik_objects_9_8_map, qik_objects_9_16_map, \
                 qik_objects_8_2_map, qik_objects_8_4_map, qik_objects_8_8_map, qik_objects_8_16_map, \
                 qik_time_avg, qik_objects_9_time_avg, qik_objects_8_time_avg, query_lst_len
    print("evaluate.py :: evaluate :: Resp :: ", str(output_str)[1:-1])

    # Auditing the results.
    with open(OUTPUT_FILE, 'a+') as f:
        f.write(str(output_str)[1:-1] + "\n")

    return qik_2_map, qik_4_map, qik_8_map, qik_16_map, qik_objects_9_2_map, qik_objects_9_4_map, qik_objects_9_8_map, qik_objects_9_16_map, qik_objects_8_2_map, qik_objects_8_4_map, qik_objects_8_8_map, qik_objects_8_16_map, qik_time_avg, qik_objects_9_time_avg, qik_objects_8_time_avg, query_lst_len


# Ref: https://gist.github.com/bwhite/3726239 - Start
def precision_at_k(r, k):
    assert k >= 1
    r = np.asarray(r)[:k] != 0
    if r.size != k:
        raise ValueError('Relevance score length < k')
    return np.mean(r)


def average_precision(r):
    r = np.asarray(r) != 0
    out = [precision_at_k(r, k + 1) for k in range(r.size) if r[k]]
    if not out:
        return 0.
    return np.mean(out)


def mean_average_precision(rs):
    return np.mean([average_precision(r) for r in rs])
# Ref: https://gist.github.com/bwhite/3726239 - End


def get_mAP(results):
    return mean_average_precision(results)


def get_binary_relevance(results, ground_truth):
    relevance_results = [1 if result in ground_truth else 0 for result in results]
    return relevance_results


# Function to get the average for a list.
def get_average(results):
    if len(results) == 0:
        return 0
    total_average = 0

    for average in results:
        total_average += average

    mean_average = total_average / len(results)
    return mean_average

def get_images(categories):
    print("evaluate.py :: get_images :: Getting images for the category set :: ", categories)

    # Return list containing all the images.
    image_list = []

    # Get all images containing given categories, select one at random.
    catIds = coco.getCatIds(catNms=categories);
    imgIds = coco.getImgIds(catIds=catIds);

    # Return if there are no images for a particular category combinaion.
    if not imgIds:
        print("evaluate.py :: get_images :: Images not present for the combination of categories.", categories)
        return None

    # Loading the annotations
    imgIds = coco.getAnnIds(imgIds=imgIds, catIds=catIds);
    anns = coco.loadAnns(imgIds)

    for ann in anns:
        img = coco.loadImgs(ann['image_id'])[0]

        if img['file_name'] not in image_subset:
            continue

        if img['file_name'] not in image_list:
            image_list.append(img['file_name'])

    # Return if there are no images for a particular category combinaion.
    if not image_list:
        print("evaluate.py :: get_images :: Images not present for the combination of categories after filtering.", categories)
        return None

    return image_list


def get_multicategory_images(image_cat_lst):
    for cat_list in image_cat_lst:
        image_list = get_images(cat_list)
        if image_list is not None:
            return image_list


def eval(category):
    global category_combination
    image_cat_lst = []

    # Check if there are multiple categories
    if "," in category:
        for cat in category.split(","):
            image_cat_lst.append(cat)
    else:
        image_cat_lst = [category]

    category_combination = '_'.join(image_cat_lst)

    # Creating the list of images for the category combination.
    image_cat_list = get_multicategory_images([image_cat_lst])

    if image_cat_list is not None:
        print("evaluate.py :: eval :: Starting evaluation with :: ", len(image_cat_list)," :: images in the category combination")
        # Starting the evaluation.
        return evaluate(image_cat_list)

    else:
        print("evaluate.py :: eval :: Cannot perform evaluation for the category combination :: ", category_combination)
        return


def evaluate_cat_comb(category_combination_file):
    print("Arun :: Entering with : ", category_combination_file)
    # 1) QIK Results List.
    qik_2_mean_average_precision_lst = []
    qik_4_mean_average_precision_lst = []
    qik_8_mean_average_precision_lst = []
    qik_16_mean_average_precision_lst = []
    qik_time_lst = []

    # 2) QIK Objects 0.9 Results List.
    qik_objects_9_2_mean_average_precision_lst = []
    qik_objects_9_4_mean_average_precision_lst = []
    qik_objects_9_8_mean_average_precision_lst = []
    qik_objects_9_16_mean_average_precision_lst = []
    qik_objects_9_time_lst = []

    # 3) QIK Objects 0.8 Results List.
    qik_objects_8_2_mean_average_precision_lst = []
    qik_objects_8_4_mean_average_precision_lst = []
    qik_objects_8_8_mean_average_precision_lst = []
    qik_objects_8_16_mean_average_precision_lst = []
    qik_objects_8_time_lst = []

    # Total queries.
    query_len_lst = []

    # Reading the category combination file.
    f = open(category_combination_file, "r")
    for cat_comb in f:
        print("evaluate.py :: evaluate_cat_comb :: Evaluating for the category combination :: ", cat_comb)

        # Evaluating with the category combination
        qik_2_map, qik_4_map, qik_8_map, qik_16_map, qik_objects_9_2_map, qik_objects_9_4_map, qik_objects_9_8_map, qik_objects_9_16_map, qik_objects_8_2_map, qik_objects_8_4_map, qik_objects_8_8_map, qik_objects_8_16_map, qik_time_avg, qik_objects_9_time_avg, qik_objects_8_time_avg, query_lst_len = eval(cat_comb.rstrip())

        # Adding QIK results.
        qik_2_mean_average_precision_lst.append(qik_2_map)
        qik_4_mean_average_precision_lst.append(qik_4_map)
        qik_8_mean_average_precision_lst.append(qik_8_map)
        qik_16_mean_average_precision_lst.append(qik_16_map)
        qik_time_lst.append(qik_time_avg)

        # Adding DIR results.
        qik_objects_9_2_mean_average_precision_lst.append(qik_objects_9_2_map)
        qik_objects_9_4_mean_average_precision_lst.append(qik_objects_9_4_map)
        qik_objects_9_8_mean_average_precision_lst.append(qik_objects_9_8_map)
        qik_objects_9_16_mean_average_precision_lst.append(qik_objects_9_16_map)
        qik_objects_9_time_lst.append(qik_objects_9_time_avg)

        # Adding LIRE results.
        qik_objects_8_2_mean_average_precision_lst.append(qik_objects_8_2_map)
        qik_objects_8_4_mean_average_precision_lst.append(qik_objects_8_4_map)
        qik_objects_8_8_mean_average_precision_lst.append(qik_objects_8_8_map)
        qik_objects_8_16_mean_average_precision_lst.append(qik_objects_8_16_map)
        qik_objects_8_time_lst.append(qik_objects_8_time_avg)

        # Adding the query length.
        query_len_lst.append(query_lst_len)

    # Obtaining the average of all the category combinations.
    print("evaluate.py :: evaluate_cat_comb :: Computing the averaget of mAP.")

    # QIK
    qik_2_average = get_average(qik_2_mean_average_precision_lst)
    qik_4_average = get_average(qik_4_mean_average_precision_lst)
    qik_8_average = get_average(qik_8_mean_average_precision_lst)
    qik_16_average = get_average(qik_16_mean_average_precision_lst)
    qik_time_average = get_average(qik_time_lst)

    # DIR
    qik_objects_9_2_average = get_average(qik_objects_9_2_mean_average_precision_lst)
    qik_objects_9_4_average = get_average(qik_objects_9_4_mean_average_precision_lst)
    qik_objects_9_8_average = get_average(qik_objects_9_8_mean_average_precision_lst)
    qik_objects_9_16_average = get_average(qik_objects_9_16_mean_average_precision_lst)
    qik_objects_9_time_average = get_average(qik_objects_9_time_lst)

    # LIRE
    qik_objects_8_2_average = get_average(qik_objects_8_2_mean_average_precision_lst)
    qik_objects_8_4_average = get_average(qik_objects_8_4_mean_average_precision_lst)
    qik_objects_8_8_average = get_average(qik_objects_8_8_mean_average_precision_lst)
    qik_objects_8_16_average = get_average(qik_objects_8_16_mean_average_precision_lst)
    qik_objects_8_time_average = get_average(qik_objects_8_time_lst)

    # Summing query lengths.
    sum_query = sum(query_len_lst)

    print("evaluate.py :: evaluate_cat_comb :: average results :: ", [qik_2_average, qik_4_average, qik_8_average, qik_16_average,
                                                        qik_objects_9_2_average, qik_objects_9_4_average, qik_objects_9_8_average, qik_objects_9_16_average,
                                                        qik_objects_8_2_average, qik_objects_8_4_average, qik_objects_8_8_average, qik_objects_8_16_average,
                                                        qik_time_average, qik_objects_9_time_average, qik_objects_8_time_average, sum_query])

    # Pretty printing the results.
    t = PrettyTable(['System', 'k=2', 'k=4', 'k=8', 'k=16', "Average Time(s)"])
    t.add_row(['QIK Captions', round(qik_2_average, 2), round(qik_4_average, 2), round(qik_8_average, 2), round(qik_16_average, 2), round(qik_time_average/1000000, 2)])
    t.add_row(['QIK Objects (0.9)', round(qik_objects_9_2_average, 2), round(qik_objects_9_4_average, 2), round(qik_objects_9_8_average, 2), round(qik_objects_9_16_average, 2), round(qik_objects_9_time_average/1000000, 2)])
    t.add_row(['QIK Objects (0.8)', round(qik_objects_8_2_average, 2), round(qik_objects_8_4_average, 2), round(qik_objects_8_8_average, 2), round(qik_objects_8_16_average, 2), round(qik_objects_8_time_average/1000000, 2)])
    print(t)
    print("Total no of queries considered = ", sum_query)


if __name__ == '__main__':
    # Setting the global variables with user input.
    parser = argparse.ArgumentParser(description='Compute MAP for pre-fetched query results.')
    parser.add_argument('-image_data', default="data/15K_Dataset.pkl", metavar='data', help='Pickled file containing the list of images.', required=False)
    parser.add_argument('-threshold', default=".70", type=float, help='Sentence similarity threshold.', required=False)
    parser.add_argument('-pre_computed_results', default="pre_constructed_data/15K_Results.pkl", help='Pre-fetched results file path.', required=False)
    parser.add_argument('-ground_truth', default="data/Ground_Truth.pkl", help='Pre-constructed ground truth.', required=False)
    parser.add_argument('-categories', default="data/2_cat_comb.txt", help='Category combination input file path.', required=False)
    parser.add_argument('-outfile', default="data/QIK_Output_Combined.txt",help='MAP output file path.', required=False)
    args = parser.parse_args()

    IMAGE_SET_PATH = args.image_data
    SIMILARITY_THRESHOLD = args.threshold
    PRE_COMPUTED_RESULTS_PATH = args.pre_computed_results
    OUTPUT_FILE = args.outfile
    PRE_COMPUTED_GROUND_TRUTH_PATH = args.ground_truth

    # Read the annotation files.
    init()

    # Performing the evaluation
    evaluate_cat_comb(args.categories)

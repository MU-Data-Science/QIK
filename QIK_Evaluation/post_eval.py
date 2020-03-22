from sys import path
path.append("../QIK_Web/util/")

from pycocotools.coco import COCO
import numpy as np
import logging
import eval_constants
import pickle
import tensorflow as tf
import tensorflow_hub as hub
import argparse

# Global variables
coco = None
coco_caps = None
image_list = []
captions_lst = []
image_subset = []
data_dict = {}
corr = None
ground_truth_dict = None
pre_computed_results = None
category_combination = None

# Local constants
SIMILARITY_THRESHOLD = .70
module_url = "https://tfhub.dev/google/universal-sentence-encoder/2"
IMAGE_SET_PATH = "data/MSCOCO_Subset_2/MSCOCO_Subset_2.pkl"
PRE_COMPUTED_RESULTS_PATH = "data/MSCOCO_Subset_2/MSCOCO_Subset_2_Results.pkl"
OUTPUT_FILE = "QIK_Output_Combined.txt"
CAT_COMB_FILE = "data/cat_comb.txt"

def init():
    global coco, coco_caps, data_dict, corr, image_subset, pre_computed_results

    # Setting log level
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename="QIK_Eval_Combined.log", level=logging.INFO)

    # Loading annotations and creating an Index
    coco=COCO(eval_constants.ANN_FILE)
    coco_caps=COCO(eval_constants.CAPTIONS_FILE)

    # Loading the subset of images.
    image_subset = pickle.load(open(IMAGE_SET_PATH, "rb"))

    # Creating a dictionary of all images and captions.
    imgIds = coco.getImgIds();

    # Iterating over all the images for obtaining all captions.
    for image in imgIds:
        cap_lst = []
        # Fetching the captions for the images fetched
        img = coco.loadImgs(image)[0]

        if img['file_name'] not in image_subset:
            continue

        annIds = coco_caps.getAnnIds(imgIds=img['id']);
        anns = coco_caps.loadAnns(annIds)

        for ann in anns:
            cap_lst.append(ann['caption'])
            captions_lst.append(ann['caption'])

        data_dict[img['file_name']] = cap_lst

    # Loading the sentence similarity model
    embed = hub.Module(module_url)

    similarity_input_placeholder = tf.placeholder(tf.string, shape=(None))
    similarity_message_encodings = embed(similarity_input_placeholder)

    # Computing the similarity between captions.
    with tf.Session() as session:
        session.run([tf.global_variables_initializer(), tf.tables_initializer()])

        message_embeddings = session.run(similarity_message_encodings,
                                         feed_dict={similarity_input_placeholder: captions_lst})
        corr = np.inner(message_embeddings, message_embeddings)
        session.close()

    # Loading the precomputed results.
    pre_computed_results = pickle.load(open(PRE_COMPUTED_RESULTS_PATH, "rb"))

def evaluate(query_lst):
    print("post_eval :: evaluate :: Starting the evaluation!")
    print("post_eval :: evaluate :: Query Images Length :: ", len(query_lst))
    print("post_eval :: evaluate :: Query Images", query_lst)

    # 1) QIK Results List.
    qik_time_lst = []

    # k=2
    qik_2_average_precision_lst = []
    qik_2_average_recall_lst = []
    qik_2_average_fscore_lst = []

    # k=4
    qik_4_average_precision_lst = []
    qik_4_average_recall_lst = []
    qik_4_average_fscore_lst = []

    # k=8
    qik_8_average_precision_lst = []
    qik_8_average_recall_lst = []
    qik_8_average_fscore_lst = []

    # k=16
    qik_16_average_precision_lst = []
    qik_16_average_recall_lst = []
    qik_16_average_fscore_lst = []

    # 1.1) QIK Objects Results List.
    qik_objects_time_lst = []

    # k=2
    qik_objects_2_average_precision_lst = []
    qik_objects_2_average_recall_lst = []
    qik_objects_2_average_fscore_lst = []

    # k=4
    qik_objects_4_average_precision_lst = []
    qik_objects_4_average_recall_lst = []
    qik_objects_4_average_fscore_lst = []

    # k=8
    qik_objects_8_average_precision_lst = []
    qik_objects_8_average_recall_lst = []
    qik_objects_8_average_fscore_lst = []

    # k=16
    qik_objects_16_average_precision_lst = []
    qik_objects_16_average_recall_lst = []
    qik_objects_16_average_fscore_lst = []

    # 2) DIR Results List.
    dir_time_lst = []

    # k=2
    dir_2_average_precision_lst = []
    dir_2_average_recall_lst = []
    dir_2_average_fscore_lst = []

    # k=4
    dir_4_average_precision_lst = []
    dir_4_average_recall_lst = []
    dir_4_average_fscore_lst = []

    # k=8
    dir_8_average_precision_lst = []
    dir_8_average_recall_lst = []
    dir_8_average_fscore_lst = []

    # k=16
    dir_16_average_precision_lst = []
    dir_16_average_recall_lst = []
    dir_16_average_fscore_lst = []

    # 3) LIRE Results List.
    lire_time_lst = []

    # k=2
    lire_2_average_precision_lst = []
    lire_2_average_recall_lst = []
    lire_2_average_fscore_lst = []

    # k=4
    lire_4_average_precision_lst = []
    lire_4_average_recall_lst = []
    lire_4_average_fscore_lst = []

    # k=8
    lire_8_average_precision_lst = []
    lire_8_average_recall_lst = []
    lire_8_average_fscore_lst = []

    # k=16
    lire_16_average_precision_lst = []
    lire_16_average_recall_lst = []
    lire_16_average_fscore_lst = []

    # 4) DELF Results List.
    delf_time_lst = []

    # k=2
    delf_2_average_precision_lst = []
    delf_2_average_recall_lst = []
    delf_2_average_fscore_lst = []

    # k=4
    delf_4_average_precision_lst = []
    delf_4_average_recall_lst = []
    delf_4_average_fscore_lst = []

    # k=8
    delf_8_average_precision_lst = []
    delf_8_average_recall_lst = []
    delf_8_average_fscore_lst = []

    # k=16
    delf_16_average_precision_lst = []
    delf_16_average_recall_lst = []
    delf_16_average_fscore_lst = []

    # 5) Deep Vision Results List.
    dv_time_lst = []

    # k=2
    dv_2_average_precision_lst = []
    dv_2_average_recall_lst = []
    dv_2_average_fscore_lst = []

    # k=4
    dv_4_average_precision_lst = []
    dv_4_average_recall_lst = []
    dv_4_average_fscore_lst = []

    # k=8
    dv_8_average_precision_lst = []
    dv_8_average_recall_lst = []
    dv_8_average_fscore_lst = []

    # k=16
    dv_16_average_precision_lst = []
    dv_16_average_recall_lst = []
    dv_16_average_fscore_lst = []

    # 6) DIR Results List.
    crow_time_lst = []

    # k=2
    crow_2_average_precision_lst = []
    crow_2_average_recall_lst = []
    crow_2_average_fscore_lst = []

    # k=4
    crow_4_average_precision_lst = []
    crow_4_average_recall_lst = []
    crow_4_average_fscore_lst = []

    # k=8
    crow_8_average_precision_lst = []
    crow_8_average_recall_lst = []
    crow_8_average_fscore_lst = []

    # k=16
    crow_16_average_precision_lst = []
    crow_16_average_recall_lst = []
    crow_16_average_fscore_lst = []

    for query_image in query_lst:
        print("post_eval :: evaluate :: Evaluation for the category combination :: %s :: with the image file :: %s" % (category_combination, query_image))
        logging.info("post_eval :: evaluate :: Evaluation for the category combination :: %s :: with the image file :: %s" % (category_combination, query_image))

        if query_image not in pre_computed_results:
            print("post_eval :: evaluate ::  Skipping evaluation for :: ", query_image)
            continue

        # Defining the ground truth - Start.
        ground_truth = []

        # Fetching the human generated captions for the image.
        human_cap_lst = data_dict[query_image]

        # Fetching the list of closest captions for each human generated caption.
        temp_cap_lst = []
        for cap in human_cap_lst:
            index = captions_lst.index(cap)

            for i, similarity in enumerate(corr[index][0:]):
                if similarity > SIMILARITY_THRESHOLD and captions_lst[i] not in temp_cap_lst:
                    temp_cap_lst.append(captions_lst[i])

            # Fetch the images having that human generated caption.
            for key in data_dict:
                for cap in data_dict[key]:
                    if cap in temp_cap_lst and key not in ground_truth:
                        ground_truth.append(key)

        print("post_eval :: evaluate :: ground_truth :: ", ground_truth)
        # Defining the ground truth - End.

        # Get QIK results
        qik_results = pre_computed_results[query_image]["qik_results"]
        print("post_eval :: evaluate :: qik_results", qik_results)
        qik_time_lst.append(pre_computed_results[query_image]["qik_time"])

        # Get QIK Objects results
        qik_objects_results = pre_computed_results[query_image]["qik_obj_results"]
        print("post_eval :: evaluate :: qik_objects_results", qik_objects_results)
        qik_objects_time_lst.append(pre_computed_results[query_image]["qik_obj_time"])

        # Get DIR results
        dir_results = pre_computed_results[query_image]["dir_results"]
        print("post_eval :: evaluate :: dir_results", dir_results)
        dir_time_lst.append(pre_computed_results[query_image]["dir_time"])

        # Get LIRE results
        lire_results = pre_computed_results[query_image]["lire_results"]
        print("post_eval :: evaluate :: lire_results", lire_results)
        lire_time_lst.append(pre_computed_results[query_image]["lire_time"])

        # Get DELF results
        delf_results = pre_computed_results[query_image]["delf_results"]
        print("post_eval :: evaluate :: delf_results", delf_results)
        delf_time_lst.append(pre_computed_results[query_image]["delf_time"])

        # Deep Vision results
        dv_results = pre_computed_results[query_image]["dv_results"]
        print("post_eval :: evaluate :: dv_results", dv_results)
        dv_time_lst.append(pre_computed_results[query_image]["dv_time"])

        # CROW results
        crow_results = pre_computed_results[query_image]["crow_results"]
        print("post_eval :: evaluate :: crow_results", crow_results)
        crow_time_lst.append(pre_computed_results[query_image]["crow_time"])

        # Computing the precision, recall and fscore.
        if len(qik_results) >= 2 and len(qik_objects_results) >=2 and len(dir_results) >= 2 and len(lire_results) >= 2 and len(delf_results) >= 2 and len(dv_results) >= 2 and len(crow_results) >= 2:
            # QIK k=2
            qik_precision, qik_recall, qik_fscore = get_metrics(qik_results[:2], ground_truth)
            qik_2_average_precision_lst.append(qik_precision)
            qik_2_average_recall_lst.append(qik_recall)
            qik_2_average_fscore_lst.append(qik_fscore)
            print("post_eval :: evaluate :: QIK,k=2,%s,%s,%f,%f,%f" % (category_combination, query_image, qik_precision, qik_recall, qik_fscore))
            logging.info("post_eval :: evaluate :: QIK,k=2,%s,%s,%f,%f,%f" % (category_combination, query_image, qik_precision, qik_recall, qik_fscore))

            # QIK Objects k=2
            qik_objects_precision, qik_objects_recall, qik_objects_fscore = get_metrics(qik_objects_results[:2], ground_truth)
            qik_objects_2_average_precision_lst.append(qik_objects_precision)
            qik_objects_2_average_recall_lst.append(qik_objects_recall)
            qik_objects_2_average_fscore_lst.append(qik_objects_fscore)
            print("post_eval :: evaluate :: QIK Objects,k=2,%s,%s,%f,%f,%f" % (category_combination, query_image, qik_objects_precision, qik_objects_recall, qik_objects_fscore))
            logging.info("post_eval :: evaluate :: QIK Objects,k=2,%s,%s,%f,%f,%f" % (category_combination, query_image, qik_objects_precision, qik_objects_recall, qik_objects_fscore))

            # DIR k=2
            dir_precision, dir_recall, dir_fscore = get_metrics(dir_results[:2], ground_truth)
            dir_2_average_precision_lst.append(dir_precision)
            dir_2_average_recall_lst.append(dir_recall)
            dir_2_average_fscore_lst.append(dir_fscore)
            print("post_eval :: evaluate :: DIR,k=2,%s,%s,%f,%f,%f" % (category_combination, query_image, dir_precision, dir_recall, dir_fscore))
            logging.info("post_eval :: evaluate :: DIR,k=2,%s,%s,%f,%f,%f" % (category_combination, query_image, dir_precision, dir_recall, dir_fscore))

            # LIRE k=2
            lire_precision, lire_recall, lire_fscore = get_metrics(lire_results[:2], ground_truth)
            lire_2_average_precision_lst.append(lire_precision)
            lire_2_average_recall_lst.append(lire_recall)
            lire_2_average_fscore_lst.append(lire_fscore)
            print("post_eval :: evaluate :: LIRE,k=2,%s,%s,%f,%f,%f" % (category_combination, query_image, lire_precision, lire_recall, lire_fscore))
            logging.info("post_eval :: evaluate :: LIRE,k=2,%s,%s,%f,%f,%f" % (category_combination, query_image, lire_precision, lire_recall, lire_fscore))

            # DELF k=2
            delf_precision, delf_recall, delf_fscore = get_metrics(delf_results[:2], ground_truth)
            delf_2_average_precision_lst.append(delf_precision)
            delf_2_average_recall_lst.append(delf_recall)
            delf_2_average_fscore_lst.append(delf_fscore)
            print("post_eval :: evaluate :: DELF,k=2,%s,%s,%f,%f,%f" % (category_combination, query_image, delf_precision, delf_recall, delf_fscore))
            logging.info("post_eval :: evaluate :: DELF,k=2,%s,%s,%f,%f,%f" % (category_combination, query_image, delf_precision, delf_recall, delf_fscore))

            # Deep Vision k=2
            dv_precision, dv_recall, dv_fscore = get_metrics(dv_results[:2], ground_truth)
            dv_2_average_precision_lst.append(dv_precision)
            dv_2_average_recall_lst.append(dv_recall)
            dv_2_average_fscore_lst.append(dv_fscore)
            print("post_eval :: evaluate :: Deep Vision,k=2,%s,%s,%f,%f,%f" % (category_combination, query_image, dv_precision, dv_recall, dv_fscore))
            logging.info("post_eval :: evaluate :: Deep Vision,k=2,%s,%s,%f,%f,%f" % (category_combination, query_image, dv_precision, dv_recall, dv_fscore))

            # CROW k=2
            crow_precision, crow_recall, crow_fscore = get_metrics(crow_results[:2], ground_truth)
            crow_2_average_precision_lst.append(crow_precision)
            crow_2_average_recall_lst.append(crow_recall)
            crow_2_average_fscore_lst.append(crow_fscore)
            print("post_eval :: evaluate :: CROW,k=2,%s,%s,%f,%f,%f" % (category_combination, query_image, crow_precision, crow_recall, crow_fscore))
            logging.info("post_eval :: evaluate :: CROW,k=2,%s,%s,%f,%f,%f" % (category_combination, query_image, crow_precision, crow_recall, crow_fscore))
        else:
            print("post_eval :: evaluate :: Skipping the query image :: ", query_image, " :: for k = 2")
            logging.info("post_eval :: evaluate :: Skipping the query image :: %s :: for k = 2" % (query_image))

        if len(qik_results) >= 4 and len(qik_objects_results) >=4 and len(dir_results) >= 4 and len(lire_results) >= 4 and len(delf_results) >= 4 and len(dv_results) >= 4 and len(crow_results) >= 4:
            # QIK k=4
            qik_precision, qik_recall, qik_fscore = get_metrics(qik_results[:4], ground_truth)
            qik_4_average_precision_lst.append(qik_precision)
            qik_4_average_recall_lst.append(qik_recall)
            qik_4_average_fscore_lst.append(qik_fscore)
            print("post_eval :: evaluate :: QIK,k=4,%s,%s,%f,%f,%f" % (category_combination, query_image, qik_precision, qik_recall, qik_fscore))
            logging.info("post_eval :: evaluate :: QIK,k=4,%s,%s,%f,%f,%f" % (category_combination, query_image, qik_precision, qik_recall, qik_fscore))

            # QIK Objects k=4
            qik_objects_precision, qik_objects_recall, qik_objects_fscore = get_metrics(qik_objects_results[:4],ground_truth)
            qik_objects_4_average_precision_lst.append(qik_objects_precision)
            qik_objects_4_average_recall_lst.append(qik_objects_recall)
            qik_objects_4_average_fscore_lst.append(qik_objects_fscore)
            print("post_eval :: evaluate :: QIK Objects,k=4,%s,%s,%f,%f,%f" % (category_combination, query_image, qik_objects_precision, qik_objects_recall, qik_objects_fscore))
            logging.info("post_eval :: evaluate :: QIK Objects,k=4,%s,%s,%f,%f,%f" % (category_combination, query_image, qik_objects_precision, qik_objects_recall, qik_objects_fscore))

            # DIR k=4
            dir_precision, dir_recall, dir_fscore = get_metrics(dir_results[:4], ground_truth)
            dir_4_average_precision_lst.append(dir_precision)
            dir_4_average_recall_lst.append(dir_recall)
            dir_4_average_fscore_lst.append(dir_fscore)
            print("post_eval :: evaluate :: DIR,k=4,%s,%s,%f,%f,%f" % (category_combination, query_image, dir_precision, dir_recall, dir_fscore))
            logging.info("post_eval :: evaluate :: DIR,k=4,%s,%s,%f,%f,%f" % (category_combination, query_image, dir_precision, dir_recall, dir_fscore))

            # LIRE k=4
            lire_precision, lire_recall, lire_fscore = get_metrics(lire_results[:4], ground_truth)
            lire_4_average_precision_lst.append(lire_precision)
            lire_4_average_recall_lst.append(lire_recall)
            lire_4_average_fscore_lst.append(lire_fscore)
            print("post_eval :: evaluate :: LIRE,k=4,%s,%s,%f,%f,%f" % (category_combination, query_image, lire_precision, lire_recall, lire_fscore))
            logging.info("post_eval :: evaluate :: LIRE,k=4,%s,%s,%f,%f,%f" % (category_combination, query_image, lire_precision, lire_recall, lire_fscore))

            # DELF k=4
            delf_precision, delf_recall, delf_fscore = get_metrics(delf_results[:4], ground_truth)
            delf_4_average_precision_lst.append(delf_precision)
            delf_4_average_recall_lst.append(delf_recall)
            delf_4_average_fscore_lst.append(delf_fscore)
            print("post_eval :: evaluate :: DELF,k=4,%s,%s,%f,%f,%f" % (category_combination, query_image, delf_precision, delf_recall, delf_fscore))
            logging.info("post_eval :: evaluate :: DELF,k=4,%s,%s,%f,%f,%f" % (category_combination, query_image, delf_precision, delf_recall, delf_fscore))

            # Deep Vision k=4
            dv_precision, dv_recall, dv_fscore = get_metrics(dv_results[:4], ground_truth)
            dv_4_average_precision_lst.append(dv_precision)
            dv_4_average_recall_lst.append(dv_recall)
            dv_4_average_fscore_lst.append(dv_fscore)
            print("post_eval :: evaluate :: Deep Vision,k=4,%s,%s,%f,%f,%f" % (category_combination, query_image, dv_precision, dv_recall, dv_fscore))
            logging.info("post_eval :: evaluate :: Deep Vision,k=4,%s,%s,%f,%f,%f" % (category_combination, query_image, dv_precision, dv_recall, dv_fscore))

            # CROW k=4
            crow_precision, crow_recall, crow_fscore = get_metrics(crow_results[:4], ground_truth)
            crow_4_average_precision_lst.append(crow_precision)
            crow_4_average_recall_lst.append(crow_recall)
            crow_4_average_fscore_lst.append(crow_fscore)
            print("post_eval :: evaluate :: CROW,k=4,%s,%s,%f,%f,%f" % (category_combination, query_image, crow_precision, crow_recall, crow_fscore))
            logging.info("post_eval :: evaluate :: DIR,k=4,%s,%s,%f,%f,%f" % (category_combination, query_image, crow_precision, crow_recall, crow_fscore))
        else:
            print("post_eval :: evaluate :: Skipping the query image :: ", query_image, " :: for k = 4")
            logging.info("post_eval :: evaluate :: Skipping the query image :: %s :: for k = 4" % (query_image))

        if len(qik_results) >= 8 and len(qik_objects_results) >=8 and len(dir_results) >= 8 and len(lire_results) >= 8 and len(delf_results) >= 8 and len(dv_results) >= 8 and len(crow_results) >= 8:
            # QIK k=8
            qik_precision, qik_recall, qik_fscore = get_metrics(qik_results[:8], ground_truth)
            qik_8_average_precision_lst.append(qik_precision)
            qik_8_average_recall_lst.append(qik_recall)
            qik_8_average_fscore_lst.append(qik_fscore)
            print("post_eval :: evaluate :: QIK,k=8,%s,%s,%f,%f,%f" % (category_combination, query_image, qik_precision, qik_recall, qik_fscore))
            logging.info("post_eval :: evaluate :: QIK,k=8,%s,%s,%f,%f,%f" % (category_combination, query_image, qik_precision, qik_recall, qik_fscore))

            # QIK Objects k=8
            qik_objects_precision, qik_objects_recall, qik_objects_fscore = get_metrics(qik_objects_results[:8], ground_truth)
            qik_objects_8_average_precision_lst.append(qik_objects_precision)
            qik_objects_8_average_recall_lst.append(qik_objects_recall)
            qik_objects_8_average_fscore_lst.append(qik_objects_fscore)
            print("post_eval :: evaluate :: QIK Objects,k=8,%s,%s,%f,%f,%f" % (category_combination, query_image, qik_objects_precision, qik_objects_recall, qik_objects_fscore))
            logging.info("post_eval :: evaluate :: QIK Objects,k=8,%s,%s,%f,%f,%f" % (category_combination, query_image, qik_objects_precision, qik_objects_recall, qik_objects_fscore))

            # DIR k=8
            dir_precision, dir_recall, dir_fscore = get_metrics(dir_results[:8], ground_truth)
            dir_8_average_precision_lst.append(dir_precision)
            dir_8_average_recall_lst.append(dir_recall)
            dir_8_average_fscore_lst.append(dir_fscore)
            print("post_eval :: evaluate :: DIR,k=8,%s,%s,%f,%f,%f" % (category_combination, query_image, dir_precision, dir_recall, dir_fscore))
            logging.info("post_eval :: evaluate :: DIR,k=8,%s,%s,%f,%f,%f" % (category_combination, query_image, dir_precision, dir_recall, dir_fscore))

            # LIRE k=8
            lire_precision, lire_recall, lire_fscore = get_metrics(lire_results[:8], ground_truth)
            lire_8_average_precision_lst.append(lire_precision)
            lire_8_average_recall_lst.append(lire_recall)
            lire_8_average_fscore_lst.append(lire_fscore)
            print("post_eval :: evaluate :: LIRE,k=8,%s,%s,%f,%f,%f" % (category_combination, query_image, lire_precision, lire_recall, lire_fscore))
            logging.info("post_eval :: evaluate :: LIRE,k=8,%s,%s,%f,%f,%f" % (category_combination, query_image, lire_precision, lire_recall, lire_fscore))

            # DELF k=8
            delf_precision, delf_recall, delf_fscore = get_metrics(delf_results[:8], ground_truth)
            delf_8_average_precision_lst.append(delf_precision)
            delf_8_average_recall_lst.append(delf_recall)
            delf_8_average_fscore_lst.append(delf_fscore)
            print("post_eval :: evaluate :: DELF,k=8,%s,%s,%f,%f,%f" % (category_combination, query_image, delf_precision, delf_recall, delf_fscore))
            logging.info("post_eval :: evaluate :: DELF,k=8,%s,%s,%f,%f,%f" % (category_combination, query_image, delf_precision, delf_recall, delf_fscore))

            # Deep Vision k=8
            dv_precision, dv_recall, dv_fscore = get_metrics(dv_results[:8], ground_truth)
            dv_8_average_precision_lst.append(dv_precision)
            dv_8_average_recall_lst.append(dv_recall)
            dv_8_average_fscore_lst.append(dv_fscore)
            print("post_eval :: evaluate :: Deep Vision,k=8,%s,%s,%f,%f,%f" % (category_combination, query_image, dv_precision, dv_recall, dv_fscore))
            logging.info("post_eval :: evaluate :: Deep Vision,k=8,%s,%s,%f,%f,%f" % (category_combination, query_image, dv_precision, dv_recall, dv_fscore))

            # CROW k=8
            crow_precision, crow_recall, crow_fscore = get_metrics(crow_results[:8], ground_truth)
            crow_8_average_precision_lst.append(crow_precision)
            crow_8_average_recall_lst.append(crow_recall)
            crow_8_average_fscore_lst.append(crow_fscore)
            print("post_eval :: evaluate :: CROW,k=8,%s,%s,%f,%f,%f" % (category_combination, query_image, crow_precision, crow_recall, crow_fscore))
            logging.info("post_eval :: evaluate :: CROW,k=8,%s,%s,%f,%f,%f" % (category_combination, query_image, crow_precision, crow_recall, crow_fscore))
        else:
            print("post_eval :: evaluate :: Skipping the query image :: ", query_image, " :: for k = 8")
            logging.info("post_eval :: evaluate :: Skipping the query image :: %s :: for k = 8" % (query_image))

        if len(qik_results) >= 16 and len(qik_objects_results) >=16 and len(dir_results) >= 16 and len(lire_results) >= 16 and len(delf_results) >= 16 and len(dv_results) >= 16 and len(crow_results) >= 16:
            # QIK k=16
            qik_precision, qik_recall, qik_fscore = get_metrics(qik_results[:16], ground_truth)
            qik_16_average_precision_lst.append(qik_precision)
            qik_16_average_recall_lst.append(qik_recall)
            qik_16_average_fscore_lst.append(qik_fscore)
            print("post_eval :: evaluate :: QIK,k=16,%s,%s,%f,%f,%f" % (category_combination, query_image, qik_precision, qik_recall, qik_fscore))
            logging.info("post_eval :: evaluate :: QIK,k=16,%s,%s,%f,%f,%f" % (category_combination, query_image, qik_precision, qik_recall, qik_fscore))

            # QIK Objects k=16
            qik_objects_precision, qik_objects_recall, qik_objects_fscore = get_metrics(qik_objects_results[:16], ground_truth)
            qik_objects_16_average_precision_lst.append(qik_objects_precision)
            qik_objects_16_average_recall_lst.append(qik_objects_recall)
            qik_objects_16_average_fscore_lst.append(qik_objects_fscore)
            print("post_eval :: evaluate :: QIK Objects,k=16,%s,%s,%f,%f,%f" % (category_combination, query_image, qik_objects_precision, qik_objects_recall, qik_objects_fscore))
            logging.info("post_eval :: evaluate :: QIK Objects,k=16,%s,%s,%f,%f,%f" % (category_combination, query_image, qik_objects_precision, qik_objects_recall, qik_objects_fscore))

            # DIR k=16
            dir_precision, dir_recall, dir_fscore = get_metrics(dir_results[:16], ground_truth)
            dir_16_average_precision_lst.append(dir_precision)
            dir_16_average_recall_lst.append(dir_recall)
            dir_16_average_fscore_lst.append(dir_fscore)
            print("post_eval :: evaluate :: DIR,k=16,%s,%s,%f,%f,%f" % (category_combination, query_image, dir_precision, dir_recall, dir_fscore))
            logging.info("post_eval :: evaluate :: DIR,k=16,%s,%s,%f,%f,%f" % (category_combination, query_image, dir_precision, dir_recall, dir_fscore))

            # LIRE k=16
            lire_precision, lire_recall, lire_fscore = get_metrics(lire_results[:16], ground_truth)
            lire_16_average_precision_lst.append(lire_precision)
            lire_16_average_recall_lst.append(lire_recall)
            lire_16_average_fscore_lst.append(lire_fscore)
            print("post_eval :: evaluate :: LIRE,k=16,%s,%s,%f,%f,%f" % (category_combination, query_image, lire_precision, lire_recall, lire_fscore))
            logging.info("post_eval :: evaluate :: LIRE,k=16,%s,%s,%f,%f,%f" % (category_combination, query_image, lire_precision, lire_recall, lire_fscore))

            # DELF k=16
            delf_precision, delf_recall, delf_fscore = get_metrics(delf_results[:16], ground_truth)
            delf_16_average_precision_lst.append(delf_precision)
            delf_16_average_recall_lst.append(delf_recall)
            delf_16_average_fscore_lst.append(delf_fscore)
            print("post_eval :: evaluate :: DELF,k=16,%s,%s,%f,%f,%f" % (category_combination, query_image, delf_precision, delf_recall, delf_fscore))
            logging.info("post_eval :: evaluate :: DELF,k=16,%s,%s,%f,%f,%f" % (category_combination, query_image, delf_precision, delf_recall, delf_fscore))

            # Deep Vision k=16
            dv_precision, dv_recall, dv_fscore = get_metrics(dv_results[:16], ground_truth)
            dv_16_average_precision_lst.append(dv_precision)
            dv_16_average_recall_lst.append(dv_recall)
            dv_16_average_fscore_lst.append(dv_fscore)
            print("post_eval :: evaluate :: Deep Vision,k=16,%s,%s,%f,%f,%f" % (category_combination, query_image, dv_precision, dv_recall, dv_fscore))
            logging.info("post_eval :: evaluate :: Deep Vision,k=16,%s,%s,%f,%f,%f" % (category_combination, query_image, dv_precision, dv_recall, dv_fscore))

            # CROW k=16
            crow_precision, crow_recall, crow_fscore = get_metrics(crow_results[:16], ground_truth)
            crow_16_average_precision_lst.append(crow_precision)
            crow_16_average_recall_lst.append(crow_recall)
            crow_16_average_fscore_lst.append(crow_fscore)
            print("post_eval :: evaluate :: CROW,k=16,%s,%s,%f,%f,%f" % (category_combination, query_image, crow_precision, crow_recall, crow_fscore))
            logging.info("post_eval :: evaluate :: CROW,k=16,%s,%s,%f,%f,%f" % (category_combination, query_image, crow_precision, crow_recall, crow_fscore))
        else:
            print("post_eval :: evaluate :: Skipping the query image :: ", query_image, " :: for k = 16")
            logging.info("post_eval :: evaluate :: Skipping the query image :: %s :: for k = 16" % (query_image))

    # Computing the mean.
    print("post_eval :: evaluate :: Computing the mean of all.")
    # 1) QIK
    # k=2
    qik_2_map = get_mean_average(qik_2_average_precision_lst)
    qik_2_mean_recall = get_mean_average(qik_2_average_recall_lst)
    qik_2_f1_score = get_mean_average(qik_2_average_fscore_lst)
    print("post_eval :: evaluate :: QIK :: k=2 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, qik_2_map, qik_2_mean_recall, qik_2_f1_score))
    logging.info("post_eval :: evaluate :: QIK :: k=2 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, qik_2_map, qik_2_mean_recall, qik_2_f1_score))

    # k=4
    qik_4_map = get_mean_average(qik_4_average_precision_lst)
    qik_4_mean_recall = get_mean_average(qik_4_average_recall_lst)
    qik_4_f1_score = get_mean_average(qik_4_average_fscore_lst)
    print("post_eval :: evaluate :: QIK :: k=4 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, qik_4_map, qik_4_mean_recall, qik_4_f1_score))
    logging.info("post_eval :: evaluate :: QIK :: k=4 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, qik_4_map, qik_4_mean_recall, qik_4_f1_score))

    # k=8
    qik_8_map = get_mean_average(qik_8_average_precision_lst)
    qik_8_mean_recall = get_mean_average(qik_8_average_recall_lst)
    qik_8_f1_score = get_mean_average(qik_8_average_fscore_lst)
    print("post_eval :: evaluate :: QIK :: k=8 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, qik_8_map, qik_8_mean_recall, qik_8_f1_score))
    logging.info("post_eval :: evaluate :: QIK :: k=8 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, qik_8_map, qik_8_mean_recall, qik_8_f1_score))

    # k=16
    qik_16_map = get_mean_average(qik_16_average_precision_lst)
    qik_16_mean_recall = get_mean_average(qik_16_average_recall_lst)
    qik_16_f1_score = get_mean_average(qik_16_average_fscore_lst)
    print("post_eval :: evaluate :: QIK :: k=16 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, qik_16_map, qik_16_mean_recall, qik_16_f1_score))
    logging.info("post_eval :: evaluate :: QIK :: k=16 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, qik_16_map, qik_16_mean_recall, qik_16_f1_score))

    qik_time_avg = get_mean_average(qik_time_lst)
    print("post_eval :: evaluate :: QIK :: Mean Average time :: %f " % (qik_time_avg))
    logging.info("post_eval :: evaluate :: QIK :: Mean Average time :: %f " % (qik_time_avg))

    # 1.1) QIK Objects
    # k=2
    qik_objects_2_map = get_mean_average(qik_objects_2_average_precision_lst)
    qik_objects_2_mean_recall = get_mean_average(qik_objects_2_average_recall_lst)
    qik_objects_2_f1_score = get_mean_average(qik_objects_2_average_fscore_lst)
    print("post_eval :: evaluate :: QIK Objects :: k=2 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, qik_objects_2_map, qik_objects_2_mean_recall, qik_objects_2_f1_score))
    logging.info("post_eval :: evaluate :: QIK Objects :: k=2 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, qik_objects_2_map, qik_objects_2_mean_recall, qik_objects_2_f1_score))

    # k=4
    qik_objects_4_map = get_mean_average(qik_objects_4_average_precision_lst)
    qik_objects_4_mean_recall = get_mean_average(qik_objects_4_average_recall_lst)
    qik_objects_4_f1_score = get_mean_average(qik_objects_4_average_fscore_lst)
    print("post_eval :: evaluate :: QIK Objects :: k=4 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, qik_objects_4_map, qik_objects_4_mean_recall, qik_objects_4_f1_score))
    logging.info("post_eval :: evaluate :: QIK Objects :: k=4 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, qik_objects_4_map, qik_objects_4_mean_recall, qik_objects_4_f1_score))

    # k=8
    qik_objects_8_map = get_mean_average(qik_objects_8_average_precision_lst)
    qik_objects_8_mean_recall = get_mean_average(qik_objects_8_average_recall_lst)
    qik_objects_8_f1_score = get_mean_average(qik_objects_8_average_fscore_lst)
    print( "post_eval :: evaluate :: QIK Objects :: k=8 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, qik_objects_8_map, qik_objects_8_mean_recall, qik_objects_8_f1_score))
    logging.info("post_eval :: evaluate :: QIK Objects :: k=8 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, qik_objects_8_map, qik_objects_8_mean_recall, qik_objects_8_f1_score))

    # k=16
    qik_objects_16_map = get_mean_average(qik_objects_16_average_precision_lst)
    qik_objects_16_mean_recall = get_mean_average(qik_objects_16_average_recall_lst)
    qik_objects_16_f1_score = get_mean_average(qik_objects_16_average_fscore_lst)
    print("post_eval :: evaluate :: QIK Objects :: k=16 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, qik_objects_16_map, qik_objects_16_mean_recall, qik_objects_16_f1_score))
    logging.info("post_eval :: evaluate :: QIK Objects :: k=16 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, qik_objects_16_map, qik_objects_16_mean_recall, qik_objects_16_f1_score))

    qik_objects_time_avg = get_mean_average(qik_objects_time_lst)
    print("post_eval :: evaluate :: QIK Objects :: Mean Average time :: %f " % (qik_objects_time_avg))
    logging.info("post_eval :: evaluate :: QIK Objects :: Mean Average time :: %f " % (qik_objects_time_avg))

    # 2) DIR
    # k=2
    dir_2_map = get_mean_average(dir_2_average_precision_lst)
    dir_2_mean_recall = get_mean_average(dir_2_average_recall_lst)
    dir_2_f1_score = get_mean_average(dir_2_average_fscore_lst)
    print("post_eval :: evaluate :: DIR :: k=2 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, dir_2_map, dir_2_mean_recall, dir_2_f1_score))
    logging.info("post_eval :: evaluate :: DIR :: k=2 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, dir_2_map, dir_2_mean_recall, dir_2_f1_score))

    # k=4
    dir_4_map = get_mean_average(dir_4_average_precision_lst)
    dir_4_mean_recall = get_mean_average(dir_4_average_recall_lst)
    dir_4_f1_score = get_mean_average(dir_4_average_fscore_lst)
    print("post_eval :: evaluate :: DIR :: k=4 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, dir_4_map, dir_4_mean_recall, dir_4_f1_score))
    logging.info("post_eval :: evaluate :: DIR :: k=4 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, dir_4_map, dir_4_mean_recall, dir_4_f1_score))

    # k=8
    dir_8_map = get_mean_average(dir_8_average_precision_lst)
    dir_8_mean_recall = get_mean_average(dir_8_average_recall_lst)
    dir_8_f1_score = get_mean_average(dir_8_average_fscore_lst)
    print("post_eval :: evaluate :: DIR :: k=8 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, dir_8_map, dir_8_mean_recall, dir_8_f1_score))
    logging.info("post_eval :: evaluate :: DIR :: k=8 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, dir_8_map, dir_8_mean_recall, dir_8_f1_score))

    # k=16
    dir_16_map = get_mean_average(dir_16_average_precision_lst)
    dir_16_mean_recall = get_mean_average(dir_16_average_recall_lst)
    dir_16_f1_score = get_mean_average(dir_16_average_fscore_lst)
    print("post_eval :: evaluate :: DIR :: k=16 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, dir_16_map, dir_16_mean_recall, dir_16_f1_score))
    logging.info("post_eval :: evaluate :: DIR :: k=16 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, dir_16_map, dir_16_mean_recall, dir_16_f1_score))

    dir_time_avg = get_mean_average(dir_time_lst)
    print("post_eval :: evaluate :: DIR :: Mean Average time :: %f " % (dir_time_avg))
    logging.info("post_eval :: evaluate :: DIR :: Mean Average time :: %f " % (dir_time_avg))

    # 3) LIRE
    # k=2
    lire_2_map = get_mean_average(lire_2_average_precision_lst)
    lire_2_mean_recall = get_mean_average(lire_2_average_recall_lst)
    lire_2_f1_score = get_mean_average(lire_2_average_fscore_lst)
    print("post_eval :: evaluate :: LIRE :: k=2 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, lire_2_map, lire_2_mean_recall, lire_2_f1_score))
    logging.info("post_eval :: evaluate :: LIRE :: k=2 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, lire_2_map, lire_2_mean_recall, lire_2_f1_score))

    # k=4
    lire_4_map = get_mean_average(lire_4_average_precision_lst)
    lire_4_mean_recall = get_mean_average(lire_4_average_recall_lst)
    lire_4_f1_score = get_mean_average(lire_4_average_fscore_lst)
    print("post_eval :: evaluate :: LIRE :: k=4 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, lire_4_map, lire_4_mean_recall, lire_4_f1_score))
    logging.info("post_eval :: evaluate :: LIRE :: k=4 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, lire_4_map, lire_4_mean_recall, lire_4_f1_score))

    # k=8
    lire_8_map = get_mean_average(lire_8_average_precision_lst)
    lire_8_mean_recall = get_mean_average(lire_8_average_recall_lst)
    lire_8_f1_score = get_mean_average(lire_8_average_fscore_lst)
    print("post_eval :: evaluate :: LIRE :: k=8 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, lire_8_map, lire_8_mean_recall, lire_8_f1_score))
    logging.info("post_eval :: evaluate :: LIRE :: k=8 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, lire_8_map, lire_8_mean_recall, lire_8_f1_score))

    # k=16
    lire_16_map = get_mean_average(lire_16_average_precision_lst)
    lire_16_mean_recall = get_mean_average(lire_16_average_recall_lst)
    lire_16_f1_score = get_mean_average(lire_16_average_fscore_lst)
    print("post_eval :: evaluate :: LIRE :: k=16 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, lire_16_map, lire_16_mean_recall, lire_16_f1_score))
    logging.info("post_eval :: evaluate :: LIRE :: k=16 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, lire_16_map, lire_16_mean_recall, lire_16_f1_score))

    lire_time_avg = get_mean_average(lire_time_lst)
    print("post_eval :: evaluate :: LIRE :: Mean Average time :: %f " % (lire_time_avg))
    logging.info("post_eval :: evaluate :: LIRE :: Mean Average time :: %f " % (lire_time_avg))

    # 4) DELF
    # k=2
    delf_2_map = get_mean_average(delf_2_average_precision_lst)
    delf_2_mean_recall = get_mean_average(delf_2_average_recall_lst)
    delf_2_f1_score = get_mean_average(delf_2_average_fscore_lst)
    print("post_eval :: evaluate :: DELF :: k=2 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, delf_2_map, delf_2_mean_recall, delf_2_f1_score))
    logging.info("post_eval :: evaluate :: DELF :: k=2 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, delf_2_map, delf_2_mean_recall, delf_2_f1_score))

    # k=4
    delf_4_map = get_mean_average(delf_4_average_precision_lst)
    delf_4_mean_recall = get_mean_average(delf_4_average_recall_lst)
    delf_4_f1_score = get_mean_average(delf_4_average_fscore_lst)
    print("post_eval :: evaluate :: DELF :: k=4 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, delf_4_map, delf_4_mean_recall, delf_4_f1_score))
    logging.info("post_eval :: evaluate :: DELF :: k=4 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, delf_4_map, delf_4_mean_recall, delf_4_f1_score))

    # k=8
    delf_8_map = get_mean_average(delf_8_average_precision_lst)
    delf_8_mean_recall = get_mean_average(delf_8_average_recall_lst)
    delf_8_f1_score = get_mean_average(delf_8_average_fscore_lst)
    print("post_eval :: evaluate :: DELF :: k=8 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, delf_8_map, delf_8_mean_recall, delf_8_f1_score))
    logging.info("post_eval :: evaluate :: DELF :: k=8 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, delf_8_map, delf_8_mean_recall, delf_8_f1_score))

    # k=16
    delf_16_map = get_mean_average(delf_16_average_precision_lst)
    delf_16_mean_recall = get_mean_average(delf_16_average_recall_lst)
    delf_16_f1_score = get_mean_average(delf_16_average_fscore_lst)
    print("post_eval :: evaluate :: DELF :: k=16 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, delf_16_map, delf_16_mean_recall, delf_16_f1_score))
    logging.info("post_eval :: evaluate :: DELF :: k=16 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, delf_16_map, delf_16_mean_recall, delf_16_f1_score))

    delf_time_avg = get_mean_average(delf_time_lst)
    print("post_eval :: evaluate :: DELF :: Mean Average time :: %f " % (delf_time_avg))
    logging.info("post_eval :: evaluate :: DELF :: Mean Average time :: %f " % (delf_time_avg))

    # 5) Deep Vision
    # k=2
    dv_2_map = get_mean_average(dv_2_average_precision_lst)
    dv_2_mean_recall = get_mean_average(dv_2_average_recall_lst)
    dv_2_f1_score = get_mean_average(dv_2_average_fscore_lst)
    print("post_eval :: evaluate :: Deep Vision :: k=2 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, dv_2_map, dv_2_mean_recall, dv_2_f1_score))
    logging.info("post_eval :: evaluate :: Deep Vision :: k=2 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, dv_2_map, dv_2_mean_recall, dv_2_f1_score))

    # k=4
    dv_4_map = get_mean_average(dv_4_average_precision_lst)
    dv_4_mean_recall = get_mean_average(dv_4_average_recall_lst)
    dv_4_f1_score = get_mean_average(dv_4_average_fscore_lst)
    print("post_eval :: evaluate :: Deep Vision :: k=4 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, dv_4_map, dv_4_mean_recall, dv_4_f1_score))
    logging.info("post_eval :: evaluate :: Deep Vision :: k=4 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, dv_4_map, dv_4_mean_recall, dv_4_f1_score))

    # k=8
    dv_8_map = get_mean_average(dv_8_average_precision_lst)
    dv_8_mean_recall = get_mean_average(dv_8_average_recall_lst)
    dv_8_f1_score = get_mean_average(dv_8_average_fscore_lst)
    print("post_eval :: evaluate :: Deep Vision :: k=8 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, dv_8_map, dv_8_mean_recall, dv_8_f1_score))
    logging.info("post_eval :: evaluate :: Deep Vision :: k=8 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, dv_8_map, dv_8_mean_recall, dv_8_f1_score))

    # k=16
    dv_16_map = get_mean_average(dv_16_average_precision_lst)
    dv_16_mean_recall = get_mean_average(dv_16_average_recall_lst)
    dv_16_f1_score = get_mean_average(dv_16_average_fscore_lst)
    print("post_eval :: evaluate :: Deep Vision :: k=16 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, dv_16_map, dv_16_mean_recall, dv_16_f1_score))
    logging.info("post_eval :: evaluate :: Deep Vision :: k=8 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, dv_16_map, dv_16_mean_recall, dv_16_f1_score))

    dv_time_avg = get_mean_average(dv_time_lst)
    print("post_eval :: evaluate :: Deep Vision :: Mean Average time :: %f " % (dv_time_avg))
    logging.info("post_eval :: evaluate :: Deep Vision :: Mean Average time :: %f " % (dv_time_avg))

    # 6) CROW
    # k=2
    crow_2_map = get_mean_average(crow_2_average_precision_lst)
    crow_2_mean_recall = get_mean_average(crow_2_average_recall_lst)
    crow_2_f1_score = get_mean_average(crow_2_average_fscore_lst)
    print("post_eval :: evaluate :: CROW :: k=2 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, crow_2_map, crow_2_mean_recall, crow_2_f1_score))
    logging.info("post_eval :: evaluate :: CROW :: k=2 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, crow_2_map, crow_2_mean_recall, crow_2_f1_score))

    # k=4
    crow_4_map = get_mean_average(crow_4_average_precision_lst)
    crow_4_mean_recall = get_mean_average(crow_4_average_recall_lst)
    crow_4_f1_score = get_mean_average(crow_4_average_fscore_lst)
    print("post_eval :: evaluate :: CROW :: k=4 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, crow_4_map, crow_4_mean_recall, crow_4_f1_score))
    logging.info("post_eval :: evaluate :: CROW :: k=4 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, crow_4_map, crow_4_mean_recall, crow_4_f1_score))

    # k=8
    crow_8_map = get_mean_average(crow_8_average_precision_lst)
    crow_8_mean_recall = get_mean_average(crow_8_average_recall_lst)
    crow_8_f1_score = get_mean_average(crow_8_average_fscore_lst)
    print("post_eval :: evaluate :: CROW :: k=8 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, crow_8_map, crow_8_mean_recall, crow_8_f1_score))
    logging.info("post_eval :: evaluate :: CROW :: k=8 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, crow_8_map, crow_8_mean_recall, crow_8_f1_score))

    # k=16
    crow_16_map = get_mean_average(crow_16_average_precision_lst)
    crow_16_mean_recall = get_mean_average(crow_16_average_recall_lst)
    crow_16_f1_score = get_mean_average(crow_16_average_fscore_lst)
    print("post_eval :: evaluate :: CROW :: k=16 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, crow_16_map, crow_16_mean_recall, crow_16_f1_score))
    logging.info("post_eval :: evaluate :: CROW :: k=16 :: Mean Average Precision :: %s :: %f :: Mean Recall :: %f :: F1 Score :: %f" % (category_combination, crow_16_map, crow_16_mean_recall, crow_16_f1_score))

    crow_time_avg = get_mean_average(crow_time_lst)
    print("post_eval :: evaluate :: CROW :: Mean Average time :: %f " % (crow_time_avg))
    logging.info("post_eval :: evaluate :: CROW :: Mean Average time :: %f " % (crow_time_avg))

    output_str = category_combination, qik_2_map, qik_4_map, qik_8_map, qik_16_map, \
                 qik_objects_2_map, qik_objects_4_map, qik_objects_8_map, qik_objects_16_map, \
                 dir_2_map, dir_4_map, dir_8_map, dir_16_map, \
                 lire_2_map, lire_4_map, lire_8_map, lire_16_map, \
                 delf_2_map, delf_4_map, delf_8_map, delf_16_map, \
                 dv_2_map, dv_4_map, dv_8_map, dv_16_map, \
                 crow_2_map, crow_4_map, crow_8_map, crow_16_map, \
                 qik_time_avg, qik_objects_time_avg, dir_time_avg, lire_time_avg, delf_time_avg, dv_time_avg, crow_time_avg, len(query_lst)

    # Auditing the results.
    with open(OUTPUT_FILE, 'a+') as f:
        f.write(str(output_str)[1:-1] + "\n")

    return str(output_str)[1:-1]

# Function to get the precision, recall and fscore for a dataset, given the ground truth.
def get_metrics(results, ground_truth):
    true_count = 0
    total = len(ground_truth)

    for result in results:
        if result in ground_truth:
            true_count += 1

    try:
        precision = true_count / len(results)
    except ZeroDivisionError:
        precision = 0

    try:
        recall = true_count / total
    except ZeroDivisionError:
        recall = 0

    try:
        fscore = 2 * precision * recall / (precision + recall)
    except ZeroDivisionError:
        fscore = 0

    return precision, recall, fscore

# Function to get the mean average for a list.
def get_mean_average(results):
    if len(results) == 0:
        return 0
    total_average = 0

    for average in results:
        total_average += average

    mean_average = total_average / len(results)
    return mean_average

def get_images(categories):
    print("post_eval :: get_images :: Getting images for the category set :: ", categories)

    # Return list containing all the images.
    image_list = []

    # Get all images containing given categories, select one at random.
    catIds = coco.getCatIds(catNms=categories);
    imgIds = coco.getImgIds(catIds=catIds);

    # Return if there are no images for a particular category combinaion.
    if not imgIds:
        print("post_eval :: get_images :: Images not present for the combination of categories.", categories)
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
        print("post_eval :: get_images :: Images not present for the combination of categories after filtering.", categories)
        return None

    return image_list

def get_multicategory_images(image_cat_lst):
    # Return list containing all the images.
    image_cat_dict = {}

    for cat_list in image_cat_lst:
        image_list = get_images(cat_list)
        if image_list is not None:
            return  image_list

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

    # Creating the ground truth.
    image_cat_list = get_multicategory_images([image_cat_lst])

    if image_cat_list is not None:
        print("post_eval :: get_images :: Starting evaluation with :: ", len(image_cat_list)," :: images in the category combination")
        # Starting the evaluation.
        resp = evaluate(image_cat_list)
        print("post_eval :: get_images :: Resp :: ", resp)
        return str(resp)
    else:
        return "post_eval :: get_images :: Ground truth images list is null"

if __name__ == '__main__':

    # Setting the global variables with user input.
    parser = argparse.ArgumentParser(description='Compute MAP for pre-fetched query results.')
    parser.add_argument('-threshold', default=".70", type=float, help='Sentence similarity threshold.', required=False)
    parser.add_argument('-preresults', default="data/MSCOCO_Subset_2/MSCOCO_Subset_2_Results.pkl", help='Pre-fetched results file path.', required=False)
    parser.add_argument('-categories', default="data/cat_comb.txt", help='Category combination input file path.', required=False)
    parser.add_argument('-outfile', default="data/QIK_Output_Combined.txt",help='MAP output file path.', required=False)
    args = parser.parse_args()

    SIMILARITY_THRESHOLD = args.threshold
    PRE_COMPUTED_RESULTS_PATH = args.preresults
    CAT_COMB_FILE = args.categories
    OUTPUT_FILE = args.outfile

    # Read the annotation files.
    init()

    # Reading the category combination from the file.
    f = open(CAT_COMB_FILE, "r")
    for cat_comb in f:
        # Evaluating with the category combination
        eval(cat_comb.rstrip())

from sys import path
path.append("../QIK_Web/util/")

import constants
import logging
import dir_search
import datetime
import argparse
import pickle

# Local constants
EVAL_K = 16

def retrieve(query_image):
    ret_dict = {}

    # Reading the input request.
    query_image_path = constants.TOMCAT_LOC + constants.IMAGE_DATA_DIR + query_image

    # Get DIR results
    time = datetime.datetime.now()

    dir_results = []

    # Fetching the candidates from DIR.
    dir_pre_results = dir_search.dir_search(query_image_path, EVAL_K + 1)

    # Noting DIR time.
    dir_time = datetime.datetime.now() - time
    print("create_dir_results.py :: DIR Fetch Execution time :: ", dir_time)
    logging.info("create_dir_results.py :: DIR Fetch Execution time :: %s", str(dir_time))

    # Removing query image from the result set.
    for res in dir_pre_results:
        img_file = res.rstrip().split("/")[-1]
        if img_file == query_image:
            continue
        dir_results.append(res.rstrip().split("/")[-1])
    print("create_dir_results.py :: DIR :: dir_results :: ", dir_results)

    # Adding data to the return dictionary.
    ret_dict["dir_time"] = dir_time.microseconds
    ret_dict["dir_results"] = dir_results
    print("create_dir_results.py :: retrieve :: ret_dict :: ", str(ret_dict))

    return ret_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Preprocess to extract text from a folder of csv files.')
    parser.add_argument('-data', default="data/15K_Dataset.pkl", metavar='data', help='Pickled file containing the list of images.', required=False)
    parser.add_argument('-out', default="data/DIR_Results.pkl", metavar='data', help='Directory to write the QIK Results.', required=False)
    args = parser.parse_args()

    # Initializing the ML Models.
    dir_search.init()

    # Initializing a dictionary to hold the results.
    results_dict = {}

    # Loading the image set.
    image_subset = pickle.load(open(args.data, "rb"))

    # Iterating over the image set.
    for image in image_subset:
        results_dict[image] = retrieve(image)

    # Creating the pickle file of the ground truth.
    with open(args.out, "wb") as f:
        pickle.dump(results_dict, f)

from sys import path
path.append("../QIK_Web/util/")

import constants
import delf_search
import datetime
import argparse
import pickle

# Local constants
EVAL_K = 16

def retrieve(query_image):
    ret_dict = {}

    # Reading the input request.
    query_image_path = constants.TOMCAT_LOC + constants.IMAGE_DATA_DIR + query_image

    # Get DELF results
    time = datetime.datetime.now()

    delf_results = []

    # Fetching the candidates from DELF.
    delf_pre_results = delf_search.delf_search(query_image_path, EVAL_K + 1)

    # Noting DELF time.
    delf_time = datetime.datetime.now() - time
    print("create_delf_results.py :: DELF Fetch Execution time :: ", delf_time)

    # Removing query image from the result set.
    for res in delf_pre_results:
        img_file = res.rstrip().split("/")[-1]
        if img_file == query_image:
            continue
        delf_results.append(res.rstrip().split("/")[-1])
    print("QIK Server :: DELF :: delf_results :: ", delf_results)

    # Adding data to the return dictionary.
    ret_dict["delf_time"] = delf_time.microseconds
    ret_dict["delf_results"] = delf_results
    print("create_delf_results.py :: retrieve :: ret_dict :: ", str(ret_dict))

    return ret_dict

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Preprocess to extract text from a folder of csv files.')
    parser.add_argument('-data', default="data/15K_Dataset.pkl", metavar='data', help='Pickled file containing the list of images.', required=False)
    parser.add_argument('-out', default="data/DELF_Results.pkl", metavar='data', help='Directory to write the QIK Results.', required=False)
    args = parser.parse_args()

    # Initializing the ML Models.
    delf_search.init()

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

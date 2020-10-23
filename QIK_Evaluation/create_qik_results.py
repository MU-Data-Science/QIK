from sys import path
path.append("../QIK_Web/util/")
path.append("../ML_Models/ObjectDetection")

import constants
from qik_search import qik_search
import caption_generator
import detect_objects
import datetime
import argparse
import pickle

# Local Constants
EVAL_K = 16

def retrieve(query_image):
    ret_dict = {}

    # Reading the input request.
    query_image_path = constants.TOMCAT_LOC + constants.IMAGE_DATA_DIR + query_image

    # Get QIK results
    time = datetime.datetime.now()

    qik_pre_results = []
    qik_results = []

    # Fetching the candidates from QIK.
    qik_results_dict = qik_search(query_image_path, obj_det_enabled=False, ranking_func='Parse Tree', fetch_count=EVAL_K + 1)
    for result in qik_results_dict:
        k, v = result
        qik_pre_results.append(k.split("::")[0].split("/")[-1])

    # Noting QIK time.
    qik_time = datetime.datetime.now() - time
    print("create_qik_results.py :: retrieve:: QIK Fetch Execution time :: ", qik_time)

    # Removing query image from the result set.
    for res in qik_pre_results:
        if res == query_image:
            continue
        qik_results.append(res)

    # Adding data to the return dictionary.
    ret_dict["qik_time"] = qik_time.microseconds
    ret_dict["qik_results"] = qik_results

    print("create_qik_results.py :: retrieve :: ret_dict :: ", str(ret_dict))
    return ret_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Preprocess to extract text from a folder of csv files.')
    parser.add_argument('-data', default="data/15K_Dataset.pkl", metavar='data', help='Pickled file containing the list of images.', required=False)
    parser.add_argument('-out', default="data/QIK_Results.pkl", metavar='data', help='Directory to write the QIK Results.', required=False)
    args = parser.parse_args()

    # Initializing the ML Models.
    caption_generator.init()
    detect_objects.init()

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

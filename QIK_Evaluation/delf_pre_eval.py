from sys import path
path.append("../QIK_Web/util/")

import constants
import logging
import delf_search
import datetime

# Local constants
EVAL_K = 16
IN_FILE = "data/MSCOCO_Subset_2/MSCOCO_Subset_2.txt"
OUT_FILE = "data/MSCOCO_Subset_2/DELF_Pre_Results_Dict.txt"

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
    print("QIK Server :: DELF Fetch Execution time :: ", delf_time)
    logging.info("QIK Server :: DELF Fetch Execution time :: %s", str(delf_time))

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

    # Writing the output to a file.
    with open(OUT_FILE, 'a+') as f:
        f.write(query_image + ":: " + str(ret_dict) + "\n")

    print("qik_pre_eval :: retrieve :: ret_dict :: ", str(ret_dict))
    return ret_dict

if __name__ == '__main__':
    # Setting log level
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename="QIK_PreEval_Server.log", level=logging.INFO)

    # Initializing the ML Models.
    delf_search.init()

    # Reading the images from the file.
    images = open(IN_FILE, "r")
    for image in images:
        print("qik_pre_eval :: Executing :: ", image)
        retrieve(image.rstrip())
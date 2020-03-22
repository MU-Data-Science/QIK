from sys import path
path.append("../QIK_Web/util/")

import constants
import logging
import dir_search
import datetime

# Local constants
EVAL_K = 16
IN_FILE = "data/MSCOCO_Subset_2/MSCOCO_Subset_2.txt"
OUT_FILE = "data/MSCOCO_Subset_2/DIR_Pre_Results_Dict.txt"

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
    print("qik_pre_eval :: DIR Fetch Execution time :: ", dir_time)
    logging.info("qik_pre_eval :: DIR Fetch Execution time :: %s", str(dir_time))

    # Removing query image from the result set.
    for res in dir_pre_results:
        img_file = res.rstrip().split("/")[-1]
        if img_file == query_image:
            continue
        dir_results.append(res.rstrip().split("/")[-1])
    print("qik_pre_eval :: DIR :: dir_results :: ", dir_results)

    # Adding data to the return dictionary.
    ret_dict["dir_time"] = dir_time.microseconds
    ret_dict["dir_results"] = dir_results

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
    dir_search.init()

    # Reading the images from the file.
    images = open(IN_FILE, "r")
    for image in images:
        print("qik_pre_eval :: Executing :: ", image)
        retrieve(image.rstrip())
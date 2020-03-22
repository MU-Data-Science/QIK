from sys import path
path.append("../QIK_Web/util/")

import constants
import logging
import requests
import datetime

# Local constants
EVAL_K = 16
IN_FILE = "data/MSCOCO_Subset_2/MSCOCO_Subset_2.txt"
OUT_FILE = "data/MSCOCO_Subset_2/LIRE_Pre_Results_Dict.txt"

def retrieve(query_image):
    ret_dict = {}

    # Reading the input request.
    query_image_path = constants.TOMCAT_LOC + constants.IMAGE_DATA_DIR + query_image

    # Get LIRE results
    time = datetime.datetime.now()

    lire_pre_results = []
    lire_results = []

    # Fetching the candidates from LIRE.
    req = constants.LIRE_QUERY + query_image_path
    resp = requests.get(req).text[1:-2].split(",")
    for img in resp:
        lire_pre_results.append(img.strip())

    # Noting LIRE time.
    lire_time = datetime.datetime.now() - time
    print("lire_pre_eval :: retrieve :: LIRE Fetch Execution time :: ", lire_time)
    logging.info("lire_pre_eval :: retrieve :: LIRE Fetch Execution time :: %s", str(lire_time))

    # Removing query image from the result set.
    for res in lire_pre_results:
        img_file = res.rstrip().split("/")[-1]
        if img_file == query_image:
            continue
        lire_results.append(res.rstrip().split("/")[-1])
    print("lire_pre_eval :: retrieve :: lire_results :: ", lire_results)

    # Adding data to the return dictionary.
    ret_dict["lire_time"] = lire_time.microseconds
    ret_dict["lire_results"] = lire_results

    # Writing the output to a file.
    with open("data/LIRE_Pre_Results_Dict.txt", 'a+') as f:
        f.write(query_image + ":: " + str(ret_dict) + "\n")

    print("lire_pre_eval :: retrieve :: ret_dict :: ", str(ret_dict))
    return ret_dict

if __name__ == '__main__':
    # Setting log level
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename="QIK_PreEval_Server.log", level=logging.INFO)

    # Reading the images from the file.
    images = open("data/MSCOCO_Subset_3.txt", "r")
    for image in images:
        print("lire_pre_eval :: Executing :: ", image)
        retrieve(image.rstrip())
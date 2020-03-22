from sys import path
path.append("../../QIK_Web/util/")

import constants
import logging
import datetime
import pickle
import numpy as np
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import pairwise_distances
from features import Extractor
from params import get_params

# Global variables
pca = None
db_feats = None

# Local constants (To be moved to eval constants)
EVAL_K = 16
IN_FILE = "../../QIK_Evaluation/data/MSCOCO_Subset_2/MSCOCO_Subset_2.txt"
OUT_FILE = "../../QIK_Evaluation/data/MSCOCO_Subset_2/Deep_Vision_Pre_Results_Dict.txt"

def get_distances(query_feats, db_feats):
    distances = pairwise_distances(query_feats, db_feats, 'cosine', n_jobs=-1)
    return distances

def deepvision_search(query_path, fetch_limit):
    print "query_path :: ", query_path
    # Get the mentioned params
    params = get_params()

    # Read image lists
    dimension = params['dimension']

    # Load featurs for the input image.
    E = Extractor(params)

    print "Extracting features for the input image."

    # Init empty np array of size 1 to store the input query features
    query_feats = np.zeros((1, dimension))

    # Extract raw feature from cnn
    feat = E.extract_feat_image(query_path).squeeze()

    # Compose single feature vector
    feat = E.pool_feats(feat)
    query_feats[0, :] = feat
    query_feats = normalize(query_feats)

    print "Computing distances"
    distances = get_distances(query_feats, db_feats)
    final_scores = distances
    print "Distances :: ", final_scores

    # Reding the db images to form a map of image and their respective scores
    with open(params['frame_list'], 'r') as f:
        database_list = f.read().splitlines()

    ranking = np.array(database_list)[np.argsort(final_scores)]
    return ranking[0][:int(fetch_limit)]

def retrieve(query_image):
    ret_dict = {}

    # Reading the input request.
    query_image_path = constants.TOMCAT_LOC + constants.IMAGE_DATA_DIR + query_image

    # Auditing the start time.
    time = datetime.datetime.now()

    # Deep Vision results
    dv_results = []

    # Fetching the candidates from Deep Vision.
    dv_pre_results = deepvision_search(query_image_path, EVAL_K + 1)

    # Noting Deep Vision time.
    dv_time = datetime.datetime.now() - time
    print("QIK Server :: Deep Vision Fetch Execution time :: ", dv_time)
    logging.info("QIK Server :: Deep Vision Fetch Execution time :: %s", str(dv_time))

    # Removing query image from the result set.
    for res in dv_pre_results:
        img_file = res.rstrip().split("/")[-1]
        if img_file == query_image:
            continue
        dv_results.append(res.rstrip().split("/")[-1])
    print("deepvision_eval ::  :: Deep Vision :: dv_results :: ", dv_results)

    # Adding data to the return dictionary.
    ret_dict["dv_time"] = dv_time.microseconds
    ret_dict["dv_results"] = dv_results

    # Writing the output to a file.
    with open(OUT_FILE, 'a+') as f:
        f.write(query_image + ":: " + str(ret_dict) + "\n")

    print("deepvision_eval ::  Results :: ", str(ret_dict))
    return ret_dict

if __name__ == '__main__':
    global pca, db_feats
    params = get_params()

    # Setting log level
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename="DeepVision_PreEval.log", level=logging.INFO)

    # PCA MODEL
    pca = pickle.load(open(params['pca_model'] + '_QIK.pkl', 'rb'))

    # Load features for the DB Images.
    db_feats = pickle.load(open(params['database_feats'], 'rb'))

    # Reading the images from the file.
    images = open(IN_FILE, "r")
    for image in images:
        print "deepvision_eval :: Executing :: ", image
        retrieve(image.rstrip())

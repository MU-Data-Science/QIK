from sys import path
path.append("../QIK_Web/util/")

import constants

from sys import path
path.append("../ML_Models/DeepImageRetrieval")

from dirtorch import extract_features, test_dir, datasets
import numpy as np

is_initialized = False
net = None
image_data = []

def init():
  print("dir_search :: init :: Start")

  global net, is_initialized, image_data

  if not is_initialized:
      is_initialized = True
      net = extract_features.load_model(constants.DIR_MODEL_PATH, 0, None)

      # Reading the file containing the images.
      for image in open(constants.DIR_CANDIDATE_IMAGE_DATA):
          image_data.append(constants.TOMCAT_IP_ADDR + constants.IMAGE_DATA_DIR + image.split("/")[-1])

def dir_search(image_file, fetch_limit):
    print("dir_search :: dir_search :: Start")

    global net, image_data

    # Writing the image to a dataset file.
    dataset = open(constants.DIR_QUERY_FILE_PATH, "w")
    dataset.write(image_file + "\n")
    dataset.flush()

    # Extracting features for the query image.
    dataset = datasets.ImageList(constants.DIR_QUERY_FILE_PATH)
    extract_features.extract_features(dataset, net, '', pooling="gem", gemp=3, output=constants.DIR_QUERY_FEATURES_FILE)

    bdescs = np.load(constants.DIR_CANDIDATES_FEATURES_FILE + '.npy')
    qdescs = np.load(constants.DIR_QUERY_FEATURES_FILE + '.npy')

    # Computing the distance matrix.
    scores = test_dir.matmul(qdescs, bdescs)

    # Get the top 20 indices
    indices = sorted(range(len(scores[0])), key=lambda i: scores[0][i])[-(fetch_limit):]

    # Preparing the return list.
    ret_lst = []
    for index in reversed(indices):
        ret_lst.append(image_data[index])

    print("dir_search :: dir_search :: ", ret_lst)
    return ret_lst
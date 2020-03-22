# Imports.
import faiss
import sys
import numpy as np
import pickle
from util import autoencoder, constants

# Dimensions. (256 X 256 X 3)
d = 196608

# No of queries.
nq = 1

# No of nearest neighbors to be fetched.
k = 20

vector_arr = []
image_arr = []
index = None
is_initialized = False

def init():
    global is_initialized
    global vector_arr
    global image_arr
    global index 

    if not is_initialized:
        is_initialized = True
        # Reading the pickle file containing the images.
        with open(constants.KNN_DICT, "rb") as fp:
            image_arr = pickle.load(fp)

        # Reading the index
        index = faiss.read_index(constants.KNN_INDEX)
        print("knn_search :: init :: index.is_trained :: ", index.is_trained)

        np.set_printoptions(threshold=sys.maxsize)

def get_nearest_images(input_img):
    global vector_arr
    global image_arr
    global index
    global model
    # Return List
    retList = [];

    # Converting the input image to a vector.
    vector = autoencoder.get_img(input_img)
    pred_vector = autoencoder.model.predict(vector)

    # Reshaping the image vector.
    reshaped_arr = pred_vector[0].reshape(d)

    # Matrix containing the query vectors.
    xq = np.vstack([reshaped_arr])
    xq[:, 0] += np.arange(nq) / 1000.

    # Actual KNN search.
    D, I = index.search(xq, k)

    # Iterating over the results.
    for ind in I[0]:
        # Appending the results to the return list.
        image_path = image_arr[ind].replace(constants.ALT_LOC, constants.TOMCAT_IP_ADDR)
        retList.append(image_path)
    return retList

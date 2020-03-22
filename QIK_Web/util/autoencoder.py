import sys
from sys import path
import numpy as np
import tflearn
from keras.preprocessing import image
import math
path.append("../ML_Models/AutoEncoder/")
import train_encoder
from util import constants

model = ''
is_initialized = False

def init():
    global model
    global is_initialized
    if not is_initialized:
        is_initialized = True
        np.set_printoptions(threshold=sys.maxsize)
        model = train_encoder.build_model()
        model = tflearn.DNN(model)
        model.load(constants.AUTO_ENC_CHECKPOINT_PATH)

def get_img(img_path):
    img = image.load_img(img_path,
                         target_size=train_encoder.IMAGE_INPUT_SIZE)
    return np.expand_dims(image.img_to_array(img), axis=0)

def getImagesScore(img1_vec, img2_vec):
    img1_pred = model.predict(img1_vec)[0]
    img2_pred = model.predict(img2_vec)[0]

    avg_1 = avg_2 = 0
    for i in range(len(img1_pred)):
        for j in range(len(img1_pred[0])):
            avg_1 += math.sqrt(sum(pow(a - b, 2) for a, b in zip(img1_pred[i][j], img2_pred[i][j])))
        avg_1 /= len(img1_pred[0])
        avg_2 += avg_1
    avg_2 /= len(img1_pred)
    return avg_2
import sys
import logging
import numpy as np
import tflearn
from keras.preprocessing import image
import math
import ast
import os
import train_encoder

np.set_printoptions(threshold=sys.maxsize)

def get_img(img_path):
    img = image.load_img(img_path,
                         target_size=train_encoder.IMAGE_INPUT_SIZE)

    return np.expand_dims(image.img_to_array(img), axis=0)

model = train_encoder.build_model()
model = tflearn.DNN(model)

checkpoint_path = 'checkpoints/model.h5'
model.load(checkpoint_path)

def euclidean_distance(x, y):
    """ return euclidean distance between two lists """
    return math.sqrt(sum(pow(a - b, 2) for a, b in zip(x, y)))
def square_rooted(x):
    return round(math.sqrt(sum([a * a for a in x])), 3)

def cosine_similarity(x, y):
    numerator = sum(a * b for a, b in zip(x, y))
    denominator = square_rooted(x) * square_rooted(y)
    return round(numerator / float(denominator), 3)

def getImagesScore(image1, image2):
    img1_vec = get_img(image1)
    img2_vec = get_img(image2)

    img1_pred = model.predict(img1_vec)[0]
    img2_pred = model.predict(img2_vec)[0]

    avg_1 = avg_2 = 0
    for i in range(len(img1_pred)):
        for j in range(len(img1_pred[0])):
            avg_1 += euclidean_distance(img1_pred[i][j], img2_pred[i][j])
        avg_1 /= len(img1_pred[0])
        avg_2 += avg_1
    avg_2 /= len(img1_pred)
    print(avg_2)
    return avg_2

print("Cand 1 Score ::", getImagesScore("images/Search_Img.png", "images/Cand_1_Img.png"))
print("Cand 2 Score ::", getImagesScore("images/Search_Img.png", "images/Cand_2_Img.png"))
print("Cand 3 Score ::", getImagesScore("images/Search_Img.png", "images/Cand_3_Img.png"))
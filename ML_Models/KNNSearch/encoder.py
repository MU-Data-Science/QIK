import sys
import tflearn
from keras.preprocessing import image
import numpy as np
sys.path.append('../AutoEncoder')
import train_encoder

np.set_printoptions(threshold=sys.maxsize)

# Loading the autoencoder model.
model = train_encoder.build_model()
model = tflearn.DNN(model)
checkpoint_path = '../AutoEncoder/checkpoints/model.h5'
model.load(checkpoint_path)

# Function to return encoded vectors for an image.
def get_img(img_path):
    img = image.load_img(img_path,target_size=train_encoder.IMAGE_INPUT_SIZE)
    return np.expand_dims(image.img_to_array(img), axis=0)

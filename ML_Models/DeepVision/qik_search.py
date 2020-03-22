from flask import Flask, request

import pickle
from sklearn.preprocessing import normalize
from params import get_params
from features import Extractor
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
import os

pca = None
db_feats = None
app = Flask(__name__)

def get_distances(query_feats, db_feats):
    distances = pairwise_distances(query_feats, db_feats, 'cosine', n_jobs=-1)
    return distances

def deepvision_search(query_path, fetch_limit):
    # Get the mentioned params
    params = get_params()
    global pca, db_feats

    # Read image lists
    dataset = params['dataset']
    image_path = params['database_images']
    dimension = params['dimension']
    pooling = params['pooling']
    N_QE = params['N_QE']
    stage = params['stage']

    # Distance type
    dist_type = params['distance']


    # Load features for the DB Images.
    db_feats = pickle.load(open(params['database_feats'], 'rb'))

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

    #return ranking[0][:int(fetch_limit)]

    # Temporary fix done for resolving the issue incurred when the number of images is less than 512.
    modified_lst = []
    for image in ranking[0]:
        # In order to increase the image count to 512, copies of images with the suffix copy are created. The below condition filters these images.
        if "copy" in image:
            continue
        modified_lst.append(image)

    return modified_lst[:int(fetch_limit)]

@app.route('/deepvision', methods=['GET', 'POST'])
def get_images():
    if request.method == 'POST':
        file = request.files['file']
        fetch_limit = request.form.get('lim')
        file.save(os.path.join('data', 'image.jpg'))
        return ' '.join(deepvision_search('data/image.jpg', fetch_limit))
    elif request.method == 'GET':
        query_path = request.args.get("query", "")
        fetch_limit = request.args.get("lim", "")
        return ' '.join(deepvision_search(query_path, fetch_limit))

if __name__ == '__main__':
    global pca, db_feats
    params = get_params()

    # PCA MODEL
    pca = pickle.load(open(params['pca_model'] + '_QIK.pkl', 'rb'))

    # Load features for the DB Images.
    db_feats = pickle.load(open(params['database_feats'], 'rb'))

    app.run(host = '0.0.0.0')
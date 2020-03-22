# Imports
import os
import caffe
import crow_constants
import extract_features
import numpy as np
import evaluate
import crow
from flask import Flask, request

# Global Variables
is_initialized = False
net = None
whitening_params = None
data = None
image_names = None
app = Flask(__name__)

# Initialization.
def init():
    global is_initialized, net, whitening_params, data, image_names

    if not is_initialized:
        net = caffe.Net(crow_constants.PROTOTXT_PATH, crow_constants.CAFFE_MODEL_PATH, caffe.TEST)

        # Checking if pre-extracted features are present.
        if not os.path.isdir(crow_constants.CROW_FEATURES_PATH):
            # Creating the features directory.
            os.mkdir(crow_constants.CROW_FEATURES_PATH)

            # Iterating over the images.
            for path in os.listdir(crow_constants.CROW_IMAGE_DIR):

                # Laoding the image..
                img = extract_features.load_img(crow_constants.CROW_IMAGE_DIR + path)

                # Skip if the image failed to load
                if img is None:
                    continue

                # Extracting features for the images
                d = extract_features.format_img_for_vgg(img)
                X = extract_features.extract_raw_features(net, "pool5", d)

                filename = os.path.splitext(os.path.basename(path))[0]
                np.save(os.path.join(crow_constants.CROW_FEATURES_PATH, filename), X)

        # Selecting the aggregation function to apply.
        agg_fn = crow.apply_crow_aggregation

        # Computing whitening params
        whitening_params = evaluate.fit_whitening(crow_constants.CROW_FEATURES_PATH, agg_fn, 128)

        # Loading the pre-extracted features.
        data, image_names = evaluate.load_and_aggregate_features(crow_constants.CROW_FEATURES_PATH, agg_fn)
        data, _ = evaluate.run_feature_processing_pipeline(np.vstack(data), params=whitening_params)

        # Setting is_initialized as True
        is_initialized = True

        print "crow_search.py :: init :: End"

def query(query_image, fetch_limit):
    print "crow_search.py :: query :: query_image :: ", query_image

    # Return List
    ret_lst = []

    # Loading the image..
    img = extract_features.load_img(crow_constants.CROW_IMAGE_DIR + query_image)

    # Extracting features for the query image.
    d = extract_features.format_img_for_vgg(img)
    net = caffe.Net(crow_constants.PROTOTXT_PATH, crow_constants.CAFFE_MODEL_PATH, caffe.TEST)
    Q = extract_features.extract_raw_features(net, "pool5", d)

    # Processing the query and ranking the results.
    agg_fn = crow.apply_crow_aggregation
    Q = agg_fn(Q)

    # Normalize and PCA to final feature
    Q, _ = crow.run_feature_processing_pipeline([Q], params=whitening_params)

    # Fetching the candidates.
    inds, dists = evaluate.get_nn(Q, data)

    for i in range(int(fetch_limit)):
        ret_lst.append(image_names[inds[i]])

    return ret_lst

@app.route('/deepvision', methods=['GET', 'POST'])
def query():
    if request.method == 'POST':
        file = request.files['file']
        fetch_limit = request.form.get('lim')
        file.save(os.path.join('data', 'image.jpg'))
        return ' '.join(query('data/image.jpg', fetch_limit))
    elif request.method == 'GET':
        query_path = request.args.get("query", "")
        fetch_limit = request.args.get("lim", "")
        return ' '.join(query(query_path, fetch_limit))


if __name__ == '__main__':
    # Initializing
    init()

    app.run(host='0.0.0.0')
# Imports
import numpy as np
from PIL import Image, ImageOps
from scipy.spatial import cKDTree
from skimage.measure import ransac
from skimage.transform import AffineTransform
import tensorflow as tf
import tensorflow_hub as hub
import glob
import os
from itertools import accumulate
import pickle
from os import path
import constants

# local constants
is_initialised = False
m = None
image_placeholder = None
module_inputs = None
module_outputs = None
d_tree = None
descriptors_agg = None
accumulated_indexes_boundaries= None
locations_agg = None
image_files_list = []
results_dict = {}

def resize_image(srcfile, destfile, new_width=256, new_height=256):
    pil_image = Image.open(srcfile)
    pil_image = ImageOps.fit(pil_image, (new_width, new_height), Image.ANTIALIAS)
    pil_image_rgb = pil_image.convert('RGB')
    pil_image_rgb.save(destfile, format='JPEG', quality=90)
    return destfile

def resize_images_folder(srcfolder, destfolder=constants.RESIZED_IMAGE_DIR, new_width=256, new_height=256):
    os.makedirs(destfolder,exist_ok=True)
    for srcfile in glob.iglob(os.path.join(srcfolder, '*')):
        src_basename = os.path.basename(srcfile)
        destfile=os.path.join(destfolder,src_basename)
        resize_image(srcfile, destfile, new_width, new_height)
    return destfolder

def image_input_fn(image_files):
    filename_queue = tf.train.string_input_producer(image_files, shuffle=False)
    reader = tf.WholeFileReader()
    _, value = reader.read(filename_queue)
    image_tf = tf.image.decode_image(value, channels=3)
    return tf.image.convert_image_dtype(image_tf, tf.float32)

def get_resized_db_image_paths(destfolder=constants.RESIZED_IMAGE_DIR):
    return sorted(list(glob.iglob(os.path.join(destfolder, '*'))))

def compute_locations_and_descriptors(image_path):
    tf.reset_default_graph()
    tf.logging.set_verbosity(tf.logging.FATAL)

    m = hub.Module(constants.DELF_MODULE_URL)

    image_placeholder = tf.placeholder(
        tf.float32, shape=(None, None, 3), name='input_image')

    module_inputs = {
        'image': image_placeholder,
        'score_threshold': 100.0,
        'image_scales': [0.25, 0.3536, 0.5, 0.7071, 1.0, 1.4142, 2.0],
        'max_feature_num': 1000,
    }

    module_outputs = m(module_inputs, as_dict=True)

    image_tf = image_input_fn([image_path])

    with tf.train.MonitoredSession() as sess:
        image = sess.run(image_tf)

        print('Extracting locations and descriptors from %s' % image_path)
        return sess.run(
            [module_outputs['locations'], module_outputs['descriptors']],
            feed_dict={image_placeholder: image})

def init():
    global m, results_dict, image_placeholder, module_inputs, module_outputs, d_tree, descriptors_agg, accumulated_indexes_boundaries, locations_agg, image_files_list, is_initialised
    if not is_initialised:
        print("Initializing DELF.")

        np.random.seed(10)
        tf.reset_default_graph()
        tf.logging.set_verbosity(tf.logging.FATAL)

        image_placeholder = tf.placeholder(tf.float32, shape=(None, None, 3), name='input_image')
        module_inputs = {
            'image': image_placeholder,
            'score_threshold': 100.0,
            'image_scales': [0.25, 0.3536, 0.5, 0.7071, 1.0, 1.4142, 2.0],
            'max_feature_num': 1000,
        }

        # Loading DELF Module.
        m = hub.Module(constants.DELF_MODULE_URL)
        module_outputs = m(module_inputs, as_dict=True)

        if not path.exists(constants.RESIZED_IMAGE_DIR):
            resize_images_folder(constants.DB_IMAGE_DIR)

        db_images = get_resized_db_image_paths()
        print(db_images)

        # Creating the index file.
        for image_path in db_images:
            image_files_list.append(constants.TOMCAT_IP_ADDR + constants.IMAGE_DATA_DIR + image_path.split("/")[-1])

        if path.exists(constants.DELF_DB_PATH):
            print("Pre computed db exists.")
            file = open(constants.DELF_DB_PATH, 'rb')
            results_dict = pickle.load(file)
            file.close()
        else :
            image_tf = image_input_fn(db_images)

            with tf.train.MonitoredSession() as sess:
                for image_path in db_images:
                    image = sess.run(image_tf)
                    print('Extracting locations and descriptors from %s' % image_path)
                    results_dict[image_path] = sess.run(
                        [module_outputs['locations'], module_outputs['descriptors']],
                        feed_dict={image_placeholder: image})

            # Storing the features.
            filehandler = open(constants.DELF_DB_PATH, "wb")
            pickle.dump(results_dict, filehandler)
            filehandler.close()

        locations_agg = np.concatenate([results_dict[constants.RESIZED_IMAGE_DIR + "/" + img.split("/")[-1]][0] for img in db_images]) # Temp Fix
        descriptors_agg = np.concatenate([results_dict[constants.RESIZED_IMAGE_DIR + "/" + img.split("/")[-1]][1] for img in db_images])
        accumulated_indexes_boundaries = list(accumulate([results_dict[constants.RESIZED_IMAGE_DIR + "/" + img.split("/")[-1]][0].shape[0] for img in db_images]))
        # locations_agg = np.concatenate([results_dict[img][0] for img in db_images])
        # descriptors_agg = np.concatenate([results_dict[img][1] for img in db_images])
        # accumulated_indexes_boundaries = list(accumulate([results_dict[img][0].shape[0] for img in db_images]))

        # Building the KD tree
        d_tree = cKDTree(descriptors_agg)
        is_initialised = True

def preprocess_query_image(query_image):
    os.makedirs(constants.DELF_QUERY_TEMP_FOLDER,exist_ok=True)
    query_basename = os.path.basename(query_image)
    destfile=os.path.join(constants.DELF_QUERY_TEMP_FOLDER,query_basename)
    resized_image = resize_image(query_image, destfile)
    return resized_image

def image_index_2_accumulated_indexes(index, accumulated_indexes_boundaries):
    if index > len(accumulated_indexes_boundaries) - 1:
        return None
    accumulated_index_start = None
    accumulated_index_end = None
    if index == 0:
        accumulated_index_start = 0
        accumulated_index_end = accumulated_indexes_boundaries[index]
    else:
        accumulated_index_start = accumulated_indexes_boundaries[index-1]
        accumulated_index_end = accumulated_indexes_boundaries[index]
    return np.arange(accumulated_index_start,accumulated_index_end)

def get_locations_2_use(image_db_index, k_nearest_indices, accumulated_indexes_boundaries, query_image_locations):
    global locations_agg

    image_accumulated_indexes = image_index_2_accumulated_indexes(image_db_index, accumulated_indexes_boundaries)
    locations_2_use_query = []
    locations_2_use_db = []
    for i, row in enumerate(k_nearest_indices):
        for acc_index in row:
            if acc_index in image_accumulated_indexes:
                locations_2_use_query.append(query_image_locations[i])
                locations_2_use_db.append(locations_agg[acc_index])
                break
    return np.array(locations_2_use_query), np.array(locations_2_use_db)

def delf_search(query_image, fetch_limit):
    ret_list = []
    global descriptors_agg, accumulated_indexes_boundaries

    resized_image = preprocess_query_image(query_image)
    query_image_locations, query_image_descriptors = compute_locations_and_descriptors(resized_image)
    distances, indices = d_tree.query(query_image_descriptors, distance_upper_bound=0.8, k=5, n_jobs=-1)
    unique_indices = np.array(list(set(indices.flatten())))
    unique_indices.sort()
    if unique_indices[-1] == descriptors_agg.shape[0]:
        unique_indices = unique_indices[:-1]

    unique_image_indexes = np.array(
        list(set([np.argmax([np.array(accumulated_indexes_boundaries) > index])
                  for index in unique_indices])))
    unique_image_indexes
    print(unique_image_indexes)

    # Array to keep track of all candidates in database.
    inliers_counts = []

    for index in unique_image_indexes:
        locations_2_use_query, locations_2_use_db = get_locations_2_use(index, indices, accumulated_indexes_boundaries, query_image_locations)
        # Perform geometric verification using RANSAC.
        _, inliers = ransac(
            (locations_2_use_db, locations_2_use_query),  # source and destination coordinates
            AffineTransform,
            min_samples=3,
            residual_threshold=20,
            max_trials=1000)
        # If no inlier is found for a database candidate image, we continue on to the next one.
        if inliers is None or len(inliers) == 0:
            continue
        # the number of inliers as the score for retrieved images.
        inliers_counts.append({"index": index, "inliers": sum(inliers)})
        print('Found inliers for image {} -> {}'.format(index, sum(inliers)))

    top_match = sorted(inliers_counts, key=lambda k: k['inliers'], reverse=True)[:fetch_limit]
    print(top_match)

    for entry in top_match:
        ret_list.append(image_files_list[int(entry["index"])])

    print("DELF return list :: ", ret_list)
    return ret_list



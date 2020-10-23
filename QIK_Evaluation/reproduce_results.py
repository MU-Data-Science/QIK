from sys import path
path.append("../QIK_Web/util/")

import constants
from qik_search import qik_search
import datetime
from pycocotools.coco import COCO
import numpy as np
import logging
import eval_constants
import pickle
import tensorflow as tf
import tensorflow_hub as hub
import argparse

# Contants
TWO_CATEGORY_COMBINATIONS = "data/2_cat_comb.txt"
THREE_CATEGORY_COMBINATIONS = "data/3_cat_comb.txt"
FOUR_CATEGORY_COMBINATIONS = "data/4_cat_comb.txt"
EVAL_K = 16

def init():
    global coco, coco_caps, data_dict, corr, image_subset, pre_computed_results

    # Loading annotations and creating an Index
    coco=COCO(eval_constants.ANN_FILE)
    coco_caps=COCO(eval_constants.CAPTIONS_FILE)

    # Loading the subset of images.
    image_subset = pickle.load(open(IMAGE_SET_PATH, "rb"))

    # Creating a dictionary of all images and captions.
    imgIds = coco.getImgIds();

    # Iterating over all the images for obtaining all captions.
    for image in imgIds:
        cap_lst = []
        # Fetching the captions for the images fetched
        img = coco.loadImgs(image)[0]

        if img['file_name'] not in image_subset:
            continue

        annIds = coco_caps.getAnnIds(imgIds=img['id']);
        anns = coco_caps.loadAnns(annIds)

        for ann in anns:
            cap_lst.append(ann['caption'])
            captions_lst.append(ann['caption'])

        data_dict[img['file_name']] = cap_lst

    # Loading the sentence similarity model
    embed = hub.Module(module_url)

    similarity_input_placeholder = tf.placeholder(tf.string, shape=(None))
    similarity_message_encodings = embed(similarity_input_placeholder)

    # Computing the similarity between captions.
    with tf.Session() as session:
        session.run([tf.global_variables_initializer(), tf.tables_initializer()])

        message_embeddings = session.run(similarity_message_encodings,
                                         feed_dict={similarity_input_placeholder: captions_lst})
        corr = np.inner(message_embeddings, message_embeddings)
        session.close()

    # Loading the precomputed results.
    pre_computed_results = pickle.load(open(PRE_COMPUTED_RESULTS_PATH, "rb"))

def eval(category):
    global category_combination
    image_cat_lst = []

    # Check if there are multiple categories
    if "," in category:
        for cat in category.split(","):
            image_cat_lst.append(cat)
    else:
        image_cat_lst = [category]

    category_combination = '_'.join(image_cat_lst)

    # Creating the ground truth.
    image_cat_list = get_multicategory_images([image_cat_lst])

    if image_cat_list is not None:
        print("post_eval :: get_images :: Starting evaluation with :: ", len(image_cat_list)," :: images in the category combination")
        # Starting the evaluation.
        resp = evaluate(image_cat_list)
        print("post_eval :: get_images :: Resp :: ", resp)
        return str(resp)
    else:
        return "post_eval :: get_images :: Ground truth images list is null"


def get_images(categories):
    print("post_eval :: get_images :: Getting images for the category set :: ", categories)

    # Return list containing all the images.
    image_list = []

    # Get all images containing given categories, select one at random.
    catIds = coco.getCatIds(catNms=categories);
    imgIds = coco.getImgIds(catIds=catIds);

    # Return if there are no images for a particular category combinaion.
    if not imgIds:
        print("post_eval :: get_images :: Images not present for the combination of categories.", categories)
        return None

    # Loading the annotations
    imgIds = coco.getAnnIds(imgIds=imgIds, catIds=catIds);
    anns = coco.loadAnns(imgIds)

    for ann in anns:
        img = coco.loadImgs(ann['image_id'])[0]

        if img['file_name'] not in image_subset:
            continue

        if img['file_name'] not in image_list:
            image_list.append(img['file_name'])

    # Return if there are no images for a particular category combinaion.
    if not image_list:
        print("post_eval :: get_images :: Images not present for the combination of categories after filtering.", categories)
        return None

    return image_lis


# Return list containing all the images.
def get_multicategory_images(image_cat_lst):
    for cat_list in image_cat_lst:
        image_list = get_images(cat_list)
        if image_list is not None:
            return  image_list

def get_images(categories):
    print("post_eval :: get_images :: Getting images for the category set :: ", categories)

    # Return list containing all the images.
    image_list = []

    # Get all images containing given categories, select one at random.
    catIds = coco.getCatIds(catNms=categories);
    imgIds = coco.getImgIds(catIds=catIds);

    # Return if there are no images for a particular category combinaion.
    if not imgIds:
        print("post_eval :: get_images :: Images not present for the combination of categories.", categories)
        return None

    # Loading the annotations
    imgIds = coco.getAnnIds(imgIds=imgIds, catIds=catIds);
    anns = coco.loadAnns(imgIds)

    for ann in anns:
        img = coco.loadImgs(ann['image_id'])[0]

        if img['file_name'] not in image_subset:
            continue

        if img['file_name'] not in image_list:
            image_list.append(img['file_name'])

    # Return if there are no images for a particular category combinaion.
    if not image_list:
        print("post_eval :: get_images :: Images not present for the combination of categories after filtering.", categories)
        return None

    return image_lis


def get_qik_results(query_image):
    ret_dict = {}

    # Reading the input request.
    query_image_path = constants.TOMCAT_LOC + constants.IMAGE_DATA_DIR + query_image

    # Get QIK results
    time = datetime.datetime.now()

    qik_pre_results = []
    qik_results = []

    # Fetching the candidates from QIK.
    qik_results_dict = qik_search(query_image_path, obj_det_enabled=False, ranking_func='Parse Tree', fetch_count=EVAL_K + 1)
    for result in qik_results_dict:
        k, v = result
        qik_pre_results.append(k.split("::")[0].split("/")[-1])

    # Noting QIK time.
    qik_time = datetime.datetime.now() - time
    print("qik_pre_eval :: retrieve:: QIK Fetch Execution time :: ", qik_time)

    # Removing query image from the result set.
    for res in qik_pre_results:
        if res == query_image:
            continue
        qik_results.append(res)

    # Adding data to the return dictionary.
    ret_dict["qik_time"] = qik_time.microseconds
    ret_dict["qik_results"] = qik_results

    print("qik_pre_eval :: retrieve :: ret_dict :: ", str(ret_dict))
    return ret_dict

if __name__ == "__main__":
    with open(TWO_CATEGORY_COMBINATIONS, 'r') as two_cat_comb:
        for combination in two_cat_comb.readlines():
            print(combination)
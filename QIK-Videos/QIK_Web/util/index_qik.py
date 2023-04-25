import os
import re
import urllib
import requests
import subprocess
import shlex
import glob
from util import constants
from util import caption_generator
from nltk.parse.stanford import StanfordDependencyParser

depParser = StanfordDependencyParser()

def print_sentence(sent_list):
    for line in sent_list:
        return line


def get_dep_tree(caption):
    dep_sentence = [parse.tree() for parse in depParser.raw_parse(caption)]
    sent = print_sentence(dep_sentence)
    dep_tree = str(sent).replace("\n", "").replace("  ", "").replace(" (", "{").replace("(", "{").replace(")",
                                                                                                          "}").replace(
        " ", "{").replace("}{", "}}{") + "}"
    return dep_tree


def add_index(video_file):
    print("index_qik.py :: add_index :: video_file :: ", video_file)

    # Loading the Show and Tell Model.
    caption_generator.init()

    # Creating the scenes for the Image.
    subprocess.call(shlex.split("scenedetect -i " + video_file + " detect-content list-scenes -n save-images"), cwd = constants.QIK_SCENES_PATH)

    # Initializing a list to hold the captions and the associated dependency trees.
    captions_lst = []
    dep_tree_lst = []

    # Iterating over the images.
    for image in glob.iglob(constants.QIK_SCENES_PATH + '/*.jpg'):
        print("index_qik.py :: add_index :: Processing image :: ", image)

        # Fetching the captions for the images using the show and tell model.
        caption = caption_generator.get_caption(image, True)

        # Handling the fullstops in captions.
        if caption[-1] == '.':
            caption = caption[:-1].strip()
        print("index_qik.py :: add_index :: caption :: ", caption)

        # Adding the caption and the dependency tree to the list.
        captions_lst.append(caption)
        dep_tree_lst.append(get_dep_tree(caption))

    # Creating the request JSON.
    json_data = {}
    json_data['key'] = video_file
    json_data['captionsArr'] = captions_lst
    json_data['depTreesArr'] = dep_tree_lst

    # Posting the captions to the index engine.
    req = constants.INDEX_ENGINE_URL + urllib.parse.quote(str(json_data))
    requests.get(req)

    print("index_qik.py :: add_index :: Finished indexing.")
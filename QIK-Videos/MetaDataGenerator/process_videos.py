# Imports
from sys import path
path.append("../QIK_Web/util")

import os
import threading
import re
import urllib
import requests
import time
import subprocess
import shlex
import glob
from threading import Thread, Lock
import constants, clip_caption_generator
from nltk.parse.stanford import StanfordDependencyParser
import extract_frames

queue = []
lock = Lock()
threadLimiter = threading.BoundedSemaphore(constants.THREAD_COUNT)
depParser = StanfordDependencyParser()


def print_sentence(sent_list):
    for line in sent_list:
        return line


def get_dep_tree(caption):
    dep_sentence = [parse.tree() for parse in depParser.raw_parse(caption)]
    sent = print_sentence(dep_sentence)
    dep_tree = str(sent).replace("\n","").replace("  ","").replace(" (","{").replace("(","{").replace(")","}").replace(" ","{").replace("}{","}}{") + "}"
    return dep_tree


# Producer Thread.
class Producer(Thread):
    def run(self):
        global queue

        # Iterating over the videso in the directory.
        for file in os.listdir(os.fsencode(constants.VIDEO_DIR)):
            # Acquiring the lock before adding the to the queue.
            lock.acquire()

            # Adding the file to the queue.
            queue.append(os.fsdecode(file))

            # Releasing the lock acquired.
            lock.release()


# Consumer Thread.
class Consumer(Thread):
    def run(self):
        global queue
        while True:
            if not queue:
                # Nothing in queue, but consumer will try to consume
                continue

            # Acquiring the lock before removing from the queue.
            lock.acquire()

            # Fetching the files from the queue.
            file = queue.pop(0)

            # Releasing the lock acquired.
            lock.release()

            # Instantiate a thread with the file name as the thread name.
            process = Process(name=file)
            process.start()
            time.sleep(1)


class Process(threading.Thread):
    def run(self):
        threadLimiter.acquire()
        try:
            self.exec()
        finally:
            threadLimiter.release()

    def exec(self):
        # Getting the complete image path
        filename = constants.VIDEO_DIR + "/" + self.getName()
        print("process_videos :: exec :: Processing :: ", filename)

        # Creating the scenes for the Image.
        subprocess.call(shlex.split("scenedetect -i " + filename + " detect-content list-scenes -n save-images -o " + constants.QIK_SCENES_PATH))
        #extract_frames.extract_key_scenes(filename, constants.QIK_SCENES_PATH)

        # Iterating over the images.
        for scene_id, scene in enumerate(sorted(glob.iglob(constants.QIK_SCENES_PATH + "/" + self.getName().split(".")[0] + '-*.jpg'))):
            print("process_videos :: exec :: Processing :: scene_id :: ", scene_id, " :: scene :: ", scene)

            # Fetching the captions for the images using the show and tell model.
            # caption_str = caption_generator.get_caption(scene).split("\n")
            # print("process_videos :: exec :: caption_str :: ", caption_str)

            # Fetching the captions for the images using the ClipCap model.
            caption_str = clip_caption_generator.get_captions(scene)
            print("process_videos :: exec :: caption_str :: ", caption_str)

            # Creating the request JSON.
            json_data = {'key': self.getName(), 'sceneId': scene_id, 'captionsArr': [caption_str],
                         'depTreesArr': [get_dep_tree(caption_str)]}

            # Posting the captions to the index engine.
            req = constants.INDEX_ENGINE_URL + urllib.parse.quote(str(json_data))
            print("process_videos :: exec :: req :: ", req)
            requests.get(req)

            # Removing the scene
           # os.system('rm -rf %s' % scene)

        print("process_videos :: exec :: Finished :: ", self.getName())


if __name__ == "__main__":
    # Loading the Captioning Model.
    clip_caption_generator.init()

    # Starting the producer process
    Producer().start()

    # Starting the consumer process.
    Consumer().start()
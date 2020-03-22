from threading import Thread, Lock
import os
import threading
from util import caption_generator
import re
import urllib
import requests
import time
from util import get_coordinates
from util import constants
from nltk.parse.stanford import StanfordDependencyParser

queue = []
lock = Lock()
threadLimiter = threading.BoundedSemaphore(constants.THREAD_COUNT)
depParser = StanfordDependencyParser()
IMAGE_DIR = constants.QUERY_IMAGE_DIR


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


# Producer Thread.
class Producer(Thread):
    def run(self):
        global queue
        global IMAGE_DIR

        # Iterating over the images in the directory.
        for file in os.listdir(os.fsencode(IMAGE_DIR)):
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
        filename = IMAGE_DIR + self.getName()
        print("Starting :: ", filename)

        # Fetching the geo co-ordinates for the images.
        meta_data = get_coordinates.ImageMetaData(filename)
        latlng = meta_data.get_lat_lng()

        # Fetching the captions for the images.
        caption_str = caption_generator.get_caption(filename, False).split("\n")

        # Forming a json data from the captions generated.
        json_data = {}

        # Adding the geo co-ordinates to the meta data
        json_data['lat'] = latlng[0]
        json_data['lng'] = latlng[1]

        caption_itr = iter(list(caption_str))
        for line in caption_itr:
            if line.startswith("Captions"):
                json_data['key'] = constants.TOMCAT_IP_ADDR + constants.IMAGE_DATA_DIR + os.fsdecode(self.getName())
                line = next(caption_itr)

                if "0)" in line:
                    cap0 = re.search(r'\S (.*?) \(', line).group(0).replace(")", "").replace("(", "").strip()
                    p0 = line.split("(")[-1].split("p=")[-1].split(")")[0]
                    if "." in cap0:
                        json_data['cap1_cap'] = cap0[:-2]
                    else:
                        json_data['cap1_cap'] = cap0
                    json_data['cap1_p'] = p0

                    # Adding the dependency tree.
                    json_data['cap1_dep_tree'] = get_dep_tree(json_data['cap1_cap'])

                    line = next(caption_itr)

                if "1)" in line:
                    cap1 = re.search(r'\S (.*?) \(', line).group(0).replace(")", "").replace("(", "").strip()
                    p1 = line.split("(")[-1].split("p=")[-1].split(")")[0]
                    if "." in cap1:
                        json_data['cap2_cap'] = cap1[:-2]
                    else:
                        json_data['cap2_cap'] = cap1
                    json_data['cap2_p'] = p1

                    # Adding the dependency tree.
                    json_data['cap2_dep_tree'] = get_dep_tree(json_data['cap2_cap'])

                    line = next(caption_itr)

                if "2)" in line:
                    cap2 = re.search(r'\S (.*?) \(', line).group(0).replace(")", "").replace("(", "").strip()
                    p2 = line.split("(")[-1].split("p=")[-1].split(")")[0]
                    if "." in cap2:
                        json_data['cap3_cap'] = cap2[:-2]
                    else:
                        json_data['cap3_cap'] = cap2
                    json_data['cap3_p'] = p2

                    # Adding the dependency tree.
                    json_data['cap3_dep_tree'] = get_dep_tree(json_data['cap3_cap'])

        print(json_data)

        # Posting the captions to the index engine.
        req = constants.INDEX_ENGINE_URL + urllib.parse.quote(str(json_data))
        requests.get(req)

        print("Finished :: ", self.getName())


def add_index(img_dir):
    global IMAGE_DIR
    IMAGE_DIR = img_dir

    # Starting the producer process
    Producer().start()

    # Starting the consumer process.
    Consumer().start()
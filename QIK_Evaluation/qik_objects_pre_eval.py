from sys import path
path.append("../QIK_Web/util/")
path.append("../ML_Models/ObjectDetection")

import constants
from qik_search import qik_search
import caption_generator
import logging
import detect_objects
import datetime
from threading import Thread, Lock
import threading
import time

# Local constants
EVAL_K = 16
IN_FILE = "data/MSCOCO_Subset_2/MSCOCO_Subset_2.txt"
OUT_FILE = "data/MSCOCO_Subset_2/QIK_Objects_9_OR_Pre_Results_Dict.txt"

# Global Variables
queue = []
process_lst = []
lock = Lock()
threadLimiter = threading.BoundedSemaphore(20)

# Consumer Thread.
class Consumer(Thread):
    def run(self):
        global queue, all_processes
        while True:
            if not queue:
                #Nothing in queue, but consumer will try to consume
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
            process_lst.append(process)

            time.sleep(1)

class Process(threading.Thread):

    def run(self):
        threadLimiter.acquire()
        try:
            self.exec()
        finally:
            threadLimiter.release()

    def exec(self):
        print("qik_pre_eval :: Process :: Executing the image :: ", self.getName())
        res = retrieve(self.getName())
        print("qik_pre_eval :: Process :: res :: ",self.getName(),",",res)

def retrieve(query_image):
    ret_dict = {}

    # Reading the input request.
    query_image_path = constants.TOMCAT_LOC + constants.IMAGE_DATA_DIR + query_image

    # Get QIK results
    time = datetime.datetime.now()

    qik_pre_results = []
    qik_results = []

    # Fetching the candidates from QIK.
    qik_results_dict = qik_search(query_image_path, obj_det_enabled=True, pure_objects_search=True, ranking_func='Parse Tree',fetch_count=EVAL_K + 1)
    for result in qik_results_dict:
        k, v = result
        qik_pre_results.append(k.split("::")[0].split("/")[-1])

    # Noting QIK time.
    qik_time = datetime.datetime.now() - time
    print("qik_pre_eval :: retrieve:: QIK Fetch Execution time :: ", qik_time)
    logging.info("qik_pre_eval :: retrieve :: QIK Fetch Execution time :: %s", str(qik_time))

    # Removing query image from the result set.
    for res in qik_pre_results:
        if res == query_image:
            continue
        qik_results.append(res)

    # Adding data to the return dictionary.
    ret_dict["qik_obj_time"] = qik_time.microseconds
    ret_dict["qik_obj_results"] = qik_results

    # Writing the output to a file.
    with open(OUT_FILE, 'a+') as f:
        f.write(query_image + ":: " + str(ret_dict) + "\n")

    print("qik_pre_eval :: retrieve :: ret_dict :: ", str(ret_dict))
    return ret_dict

def fetch_images():
    print()

if __name__ == '__main__':
    # Setting log level
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename="QIK_PreEval_Server.log", level=logging.INFO)

    # Initializing the ML Models.
    caption_generator.init()
    detect_objects.init()

    # Starting the consumer.
    print("qik_pre_eval :: main :: Starting Client")
    Consumer().start()

    # Reading the category combination from the file.
    images = open(IN_FILE, "r")
    for image in images:
        print("qik_pre_eval :: Executing :: ", image)

        # Acquiring the lock before adding the to the queue.
        lock.acquire()

        # Adding the file to the queue.
        queue.append(image.rstrip())

        # Releasing the lock acquired.
        lock.release()

    # Waiting for processes to complete.
    time.sleep(100)
    exit_codes = [p.join() for p in process_lst]
    print("qik_pre_eval :: exit_codes :: ", exit_codes)
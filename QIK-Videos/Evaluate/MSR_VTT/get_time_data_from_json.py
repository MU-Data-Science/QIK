from sys import path
path.append("/mydata/QIK-Videos/APTED/apted")
path.append("/mydata/QIK-Videos/QIK_Web/util/")

import os
import threading
import json
import time
from threading import Thread, Lock

THREAD_COUNT = 100
VIDEO_LIST_FILE = 'QIK_Index_Engine_Results_With_Optimized_Times.txt'
RESULTS_FILE_PREFIX = 'qik_msrvtt_q_testset_d_trainvalset_ted_weighed_ranked_optimized_times'

queue = []
lock = Lock()
threadLimiter = threading.BoundedSemaphore()

# Producer Thread.
class Producer(Thread):
    def run(self):
        global queue

        if os.path.exists(VIDEO_LIST_FILE):
            # Iterating over the images mentioned in the file.
            videos = open(VIDEO_LIST_FILE, "r")
            for video in videos:
                # Acquiring the lock before adding the to the queue.
                lock.acquire()

                # Adding the file to the queue.
                queue.append(os.fsdecode(video.rstrip()))

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
        line = self.getName().split("::")

        # Obtaining the video and response
        query = line[0]
        resp = line[1].replace("{'", "{\"").replace("'}", "\"}").replace(", '", ", \"").replace("', ", "\", ").replace(": '", ": \"").replace("': ", "\": ").replace("['", "[\"").replace("']", "\"]")

        # Interpreting the response as a json object
        stored_res = json.loads(resp)

        # Obtaining the time data
        scene_detect_time = stored_res['sceneDetectTime']
        captioning_time = stored_res["captioningTime"]
        retrieval_time = stored_res["dbRetrievalTime"]
        ranking_time = stored_res["rankingTime"]
        total_time = scene_detect_time + captioning_time + retrieval_time + ranking_time

        # Writing results to the file
        with open(RESULTS_FILE_PREFIX + ".csv", 'a+') as f:
            f.write(query + "," + str(scene_detect_time) + "," +  str(captioning_time) + "," + str(retrieval_time) + "," + str(ranking_time) + "," + str(total_time) + "\n")


if __name__ == "__main__":
    # Starting the producer process
    Producer().start()

    # Starting the consumer process.
    Consumer().start()
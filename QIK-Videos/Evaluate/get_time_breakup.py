from sys import path

import argparse
import os
import threading
import json
import time
from threading import Thread, Lock

VIDEO_LIST_FILE = 'QIK_Index_Engine_Results_With_Optimized_Times.txt'
RESULTS_FILE_PREFIX = 'qik_msrvtt_q_testset_d_trainvalset_ted_weighed_ranked_optimized_times'

queue = []
lock = Lock()
threadLimiter = threading.BoundedSemaphore()

def get_average(results):
    """
    Function to get the average for a list.
    
    :param results: list of numbers 
    :return: average
    """

    if len(results) == 0:
        return 0
    total_average = 0

    for average in results:
        total_average += average

    mean_average = total_average / len(results)
    return mean_average

def get_query_lst(query_lst):
    ret_lst = []
    with open(query_lst, "r") as file:
        for video in file:
            ret_lst.append(video.rstrip())
    return ret_lst

def get_time_data(inp):
    # Getting the complete image path
    line = inp.split("::")

    # Obtaining the video and response
    query = line[0].split("/")[-1]
    resp = line[1].replace("{'", "{\"").replace("'}", "\"}").replace(", '", ", \"").replace("', ", "\", ").replace(": '", ": \"").replace("': ", "\": ").replace("['", "[\"").replace("']", "\"]")

    # Interpreting the response as a json object
    stored_res = json.loads(resp)

    # Obtaining the time data
    scene_detect_time = stored_res['sceneDetectTime']
    captioning_time = stored_res["captioningTime"]
    retrieval_time = stored_res["dbRetrievalTime"]
    ranking_time = stored_res["rankingTime"]
    total_time = scene_detect_time + captioning_time + retrieval_time + ranking_time

    return query, scene_detect_time, captioning_time, retrieval_time, ranking_time, total_time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Obtain time take for each step')
    parser.add_argument('-video_data', default="data/MSR_VTT_Query_Files.txt", metavar='data', help='File containing the list of videos', required=False)
    parser.add_argument('-data', default="pre_constructed_data/QIK_Retrieval_Time_Breakup.txt", metavar='data', help='Data File', required=False)
    args = parser.parse_args()

    scene_detect_time_lst, captioning_time_lst, retrieval_time_lst, ranking_time_lst, total_time_lst = [], [], [], [], []

    query_lst = get_query_lst(args.video_data)

    with open(args.data, "r") as videos:
        for video in videos:
            
            try:
                query, scene_detect_time, captioning_time, retrieval_time, ranking_time, total_time = get_time_data(video)
            except:
                print("Eception encountered processing :: ", video)
                continue


            if query in query_lst:
                scene_detect_time_lst.append(scene_detect_time)
                captioning_time_lst.append(captioning_time)
                retrieval_time_lst.append(retrieval_time)
                ranking_time_lst.append(ranking_time)
                total_time_lst.append(total_time)

    avg_scene_detect_time = get_average(scene_detect_time_lst)
    avg_captioning_time = get_average(captioning_time_lst)
    avg_retrieval_time = get_average(retrieval_time_lst)
    avg_ranking_time = get_average(ranking_time_lst)
    avg_total_time = get_average(total_time_lst)

    print("Average Scene Detection Time (s) : ", avg_scene_detect_time)
    print("Average Captioning Time (s) : ", avg_captioning_time)
    print("Average Retrieval Time (s) : ", avg_retrieval_time)
    print("Average Ranking Time (s) : ", avg_ranking_time)
    print("Average of Total Time Taken (s) : ", avg_total_time)
    
from sys import path
path.append("../APTED/apted")
path.append("util/")

import sys
import clip_caption_generator
import constants
import json
import requests
import datetime
import subprocess
import shlex
import urllib
import glob
import os
import extract_frames
import threading
import mlpy
import parse_show_tree
import detect_scenes
from apted import APTED, PerEditOperationConfig
from concurrent.futures import ThreadPoolExecutor
import apted.helpers as apth


def get_caption(image, caption_dict, scene_seq):
    # Generating the captions.
    caption = clip_caption_generator.get_captions(image)

    # Handling the fullstops in captions ().
    if caption[-1] == '.':
        caption = caption[:-1].strip()

    # Adding to the dictionary.
    caption_dict[scene_seq] = caption

def rank_scene_match(video, video_scenes_list, video_scene_match_lst):
    video_scene_match_lst.append((video, len(video_scenes_list)))

def rank_lcs(video, cap_lst, video_scenes_list, video_lcs_lst):
    lcs_length, _ = mlpy.lcs_std(cap_lst, video_scenes_list)
    video_lcs_lst.append((video, lcs_length))

def rank_ted_and_lcs(video, cap_lst, cap_parse_tree_lst, res, video_scenes_list, video_ted_and_lcs_lst):
    video_ted = 0

    lcs_length, path = mlpy.lcs_std(cap_lst, video_scenes_list)

    for p1, p2 in zip(path[0], path[1]):
        query_parse_tree = cap_parse_tree_lst[p1]
        scene_ret_lst = res[video_scenes_list[p2]]
        for scene_ret_data in scene_ret_lst:
            if scene_ret_data['fileURL'] == video:
                scene_parse_tree = scene_ret_data['parseTree']

                parseTED = APTED(apth.Tree.from_text(query_parse_tree), apth.Tree.from_text(scene_parse_tree),
                                 PerEditOperationConfig(1, 1, 1)).compute_edit_distance()
                video_ted += 1 / (1 + parseTED)
                break

    video_ted_and_lcs_lst.append((video, video_ted, lcs_length))

def rank_scene_match_ted_and_lcs(video, cap_lst, cap_parse_tree_lst, res, video_scenes_list, video_ted_and_lcs_lst):
    video_ted = 0

    _, path = mlpy.lcs_std(cap_lst, video_scenes_list)

    for p1, p2 in zip(path[0], path[1]):
        query_parse_tree = cap_parse_tree_lst[p1]
        scene_ret_lst = res[video_scenes_list[p2]]
        for scene_ret_data in scene_ret_lst:
            if scene_ret_data['fileURL'] == video:
                scene_parse_tree = scene_ret_data['parseTree']

                parseTED = APTED(apth.Tree.from_text(query_parse_tree), apth.Tree.from_text(scene_parse_tree),
                                 PerEditOperationConfig(1, 1, 1)).compute_edit_distance()
                video_ted += 1 / (1 + parseTED)
                break

    video_ted_and_lcs_lst.append((video, video_ted, len(video_scenes_list)))


def qik_search(query_video, fetch_count=None, ranking_func="ted_and_lcs"):
    # Initializing a list to hold the captions, associated dependency trees and sorted results.
    captions_dict = {}
    sorted_cand_video_dict = []

    # Initial Loading of the models.
    clip_caption_generator.init()
    parse_show_tree.init()

    # Deleting scenes detected during previous executions
    os.system('rm -rf %s/*' % constants.QIK_SCENES_PATH)

    # Dictionary to audit data for future use
    audit_dict = {'query': query_video}

    # Noting the time taken for further auditing.
    start_time = datetime.datetime.now()

    # Detecting key scenes of the input video.
    # subprocess.call(shlex.split("scenedetect -i " + query_video + " detect-content list-scenes -n save-images -o " + constants.QIK_SCENES_PATH))
    detect_scenes.obtain_scenes(query_video)
    # extract_frames.extract_key_scenes(query_video, constants.QIK_SCENES_PATH)

    # Noting the scene detect time for further auditing.
    scene_detect_time = datetime.datetime.now()
    audit_dict['sceneDetectTime'] = (scene_detect_time - start_time).total_seconds()

    # Iterating over the scenes detected.
    with ThreadPoolExecutor(max_workers=1) as exe:
        for counter, image in enumerate(glob.iglob(constants.QIK_SCENES_PATH + '/*.jpg')):
            exe.submit(get_caption, image, captions_dict, counter)

    # Obtaining the captions list.
    captions_lst = [captions_dict[key] for key in sorted(captions_dict)]

    # Creating the request JSON.
    json_data = {'captionsArr': captions_lst}

    # Noting the captioning time for further auditing.
    captioning_time = datetime.datetime.now()
    audit_dict['captioningTime'] = (captioning_time - scene_detect_time).total_seconds()

    # POST Request
    # res = requests.post(constants.INDEX_ENGINE_QUERY_URL, data=json.dumps(json_data), headers={'Content-Type': 'application/json', 'Accept':'application/json'}, timeout=7200).text
    cap_res = requests.post(constants.INDEX_ENGINE_QUERY_URL, data=json.dumps(json_data), headers={'Content-Type': 'application/json', 'Accept':'application/json'}).text

    # Noting the database retrieval time for further auditing.
    db_retrieval_time = datetime.datetime.now()
    audit_dict['dbRetrievalTime'] = (db_retrieval_time - captioning_time).total_seconds()

    # Forming the return image set.
    if cap_res is not None:
        video_scene_dict = {}

        # Interpreting the response as a json object
        res = json.loads(cap_res)

        # Obtaining the query results
        query_res = res['queryResults']

        if query_res is not None:
            # Creating the captions for each video
            for cap_id in query_res:
                for video in query_res[cap_id]:
                    if video['fileURL'] in video_scene_dict:
                        video_scene_dict[video['fileURL']].append((cap_id))
                    else:
                        video_scene_dict[video['fileURL']] = [(cap_id)]
            
            if ranking_func == "scene_match":
                # Obtaining the candidate scores
                video_scene_match_lst = []
                with ThreadPoolExecutor() as exe:
                    for video in video_scene_dict:
                        exe.submit(rank_scene_match, video, video_scene_dict[video], video_scene_match_lst)

                # Ranking the candidates
                sorted_cand_video_dict = sorted(video_scene_match_lst, key=lambda x: (x[1]), reverse=True)

            elif ranking_func == "lcs":
                # Converting the list of captions to list of scene ids.
                cap_lst = [i for i in range(1, len(captions_lst) + 1)]

                # Obtaining the candidate scores
                video_lcs_lst = []
                with ThreadPoolExecutor() as exe:
                    for video in video_scene_dict:
                        exe.submit(rank_lcs, video, cap_lst, video_scene_dict[video], video_lcs_lst)

                # Ranking the candidates
                sorted_cand_video_dict = sorted(video_lcs_lst, key=lambda x: (x[1]), reverse=True)

            elif ranking_func == "ted_and_lcs":
                # Converting the list of captions to list of scene ids.
                cap_lst = [i for i in range(1, len(captions_lst) + 1)]

                # Obtaining the parse tree representations
                cap_parse_tree_lst = res['querySceneParseTrees']

                # Done for LCS and total number of scene matches:
                video_lcs_lst = []

                with ThreadPoolExecutor(max_workers=1000) as exe:
                    for video in video_scene_dict:
                        # Ranking the candidate videos
                        exe.submit(rank_ted_and_lcs, video, cap_lst, cap_parse_tree_lst, query_res, video_scene_dict[video], video_lcs_lst)

                sorted_cand_video_dict = sorted(video_lcs_lst, key=lambda x: (x[1], x[2]), reverse=True)

            elif ranking_func == "scene_match_ted_and_lcs":
                # Converting the list of captions to list of scene ids.
                cap_lst = [i for i in range(1, len(captions_lst) + 1)]

                # Obtaining the parse tree representations
                cap_parse_tree_lst = res['querySceneParseTrees']

                # Done for LCS and total number of scene matches:
                video_lcs_lst = []

                with ThreadPoolExecutor(max_workers=1000) as exe:
                    for video in video_scene_dict:
                        # Ranking the candidate videos
                        exe.submit(rank_scene_match_ted_and_lcs, video, cap_lst, cap_parse_tree_lst, query_res, video_scene_dict[video], video_lcs_lst)

                sorted_cand_video_dict = sorted(video_lcs_lst, key=lambda x: (x[1], x[2]), reverse=True)

    # Noting the database retrieval time for further auditing.
    ranking_time = datetime.datetime.now()
    audit_dict['rankingTime'] = (ranking_time - db_retrieval_time).total_seconds()

    # Writing the response to a file
    if cap_res is not None:
        with open("QIK_Retrieval_Time_Breakup.txt", 'a+') as f:
            f.write(query_video + "::" + str(audit_dict) + "\n")

    if sorted_cand_video_dict and fetch_count is not None:
        return sorted_cand_video_dict[:fetch_count]
    else:
        return sorted_cand_video_dict

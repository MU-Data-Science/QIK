from sys import path
path.append("../APTED/apted")
path.append("util/")

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
import mlpy


def qik_search(query_video, fetch_count=None):
    obj_res = None

    captionRanksDict = {}
    sortedCaptionRanksDict = {}

    # Noting the time taken for further auditing.
    time = datetime.datetime.now()

    # Initial Loading of the caption generator model.
    clip_caption_generator.init()

    # Deleting scenes detected during previous executions
    os.system('rm -rf %s/*' % constants.QIK_SCENES_PATH)

    # Detecting key scenes of the input video.
    subprocess.call(shlex.split("scenedetect -i " + query_video + " detect-content list-scenes -n save-images -o " + constants.QIK_SCENES_PATH))
    # extract_frames.extract_key_scenes(query_video, constants.QIK_SCENES_PATH)

    # Initializing a list to hold the captions and the associated dependency trees.
    captions_lst = []

    # Iterating over the scenes detected.
    for image in glob.iglob(constants.QIK_SCENES_PATH + '/*.jpg'):

        # Generating the captions.
        caption = clip_caption_generator.get_captions(image)

        # Handling the fullstops in captions.
        if caption[-1] == '.':
            caption = caption[:-1].strip()
        print("qik_search.py :: qik_search :: caption :: ", caption)

        # Adding the caption to the list.
        captions_lst.append(caption)

    # Creating the request JSON.
    json_data = {'captionsArr': captions_lst}

    # Querying the backend to fetch the list of images and captions.
    # GET Request
    # cap_req = constants.INDEX_ENGINE_QUERY_URL + urllib.parse.quote(str(json_data))
    # print("qik_search.py :: qik_search :: QIK Captions Request :: ", cap_req)
    # cap_res = requests.get(cap_req).text

    # POST Request
    print("qik_search.py :: qik_search :: json_data :: ", json_data)
    res = requests.post(constants.INDEX_ENGINE_QUERY_URL, data=json.dumps(json_data), headers={'Content-Type': 'application/json', 'Accept':'application/json'}, timeout=7200).text

    cap_res = requests.post(constants.INDEX_ENGINE_QUERY_URL, data=json.dumps(json_data), headers={'Content-Type': 'application/json', 'Accept':'application/json'}).text
    print("qik_search.py :: qik_search :: cap_res :: ", cap_res)

    # Forming the return image set.
    if cap_res is not None:
        video_capt_dict = {}
        video_lcs_dict = {}

        # Interpreting the response as a json object
        res = json.loads(cap_res)

        # Converting the list of captions to list of scene ids.
        cap_lst = [i for i in range(1, len(captions_lst) + 1)]

        # Creating the captions for each video
        for resMap in res:
            if resMap['fileURL'] in video_capt_dict:
                video_capt_dict[resMap['fileURL']].append(int(resMap['sceneId']))
            else:
                video_capt_dict[resMap['fileURL']] = [int(resMap['sceneId'])]

        print("video_capt_dict :: Before :: ", video_capt_dict)

        for video in video_capt_dict:
            cand_lst = video_capt_dict[video]
            sorted_cand_lst = sorted(cand_lst)

            # Creating a map for the ids
            id_dict = {}
            count = 1
            for cand in sorted_cand_lst:
                if cand not in id_dict:
                    id_dict[cand] = count
                    count += 1

            cand_id_lst = [id_dict[cand] for cand in cand_lst]

            length, path = mlpy.lcs_std(cap_lst, cand_id_lst)
            video_lcs_dict[video] = length

        sorted_video_lcs_dict = sorted(video_lcs_dict.items(), key=lambda kv: kv[1], reverse=True)

    # Auditing the QIK execution time.
    print("qik_search.py :: qik_search :: QIK Execution time :: ", (datetime.datetime.now() - time))

    if sorted_video_lcs_dict and fetch_count is not None:
        print("qik_search.py :: qik_search :: sorted_video_lcs_dict :: ", sorted_video_lcs_dict[:fetch_count])
        return sorted_video_lcs_dict[:fetch_count]
    else:
        print("qik_search.py :: qik_search :: sorted_video_lcs_dict :: ", sorted_video_lcs_dict)
        return sorted_video_lcs_dict
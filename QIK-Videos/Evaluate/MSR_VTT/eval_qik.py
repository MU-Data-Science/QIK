# Imports
from sys import path
path.append("../QIK_Web/util")
path.append("../ML_Models/ShowAndTell/im2txt")

import os
import qik_search
import pickle
import numpy as np
import traceback
import clip_caption_generator
import time

# Constants/Configurations
QUERY_DIR = "/mydata/MSR_VTT/TestVideo"
GROUND_TRUTH = "MSR_VTT/MSRVTT_Temp_Regrouped_Categories_Ground_Truth_10.pkl"
RESULTS_FILE_PREFIX = "MSR_VTT/qik_msrvtt_q_testset_d_trainvalset_results"

# Ref: https://gist.github.com/bwhite/3726239 - Start
def precision_at_k(r, k):
    assert k >= 1
    r = np.asarray(r)[:k] != 0
    if r.size != k:
        raise ValueError('Relevance score length < k')
    return np.mean(r)


def average_precision(r):
    r = np.asarray(r) != 0
    out = [precision_at_k(r, k + 1) for k in range(r.size) if r[k]]
    if not out:
        return 0.
    return np.mean(out)


def mean_average_precision(rs):
    return np.mean([average_precision(r) for r in rs])
# Ref: https://gist.github.com/bwhite/3726239 - End


def get_mAP(results):
    return mean_average_precision(results)


def get_binary_relevance(results, ground_truth):
    relevance_results = [1 if result in ground_truth else 0 for result in results]
    return relevance_results


def get_ground_truth(video_id, groundtruth):
    for category in groundtruth:
        if video_id in groundtruth[category]:
            return groundtruth[category]


def get_query_list():
    query_lst = []

    # Iterating over the video directory
    for filename in os.listdir(QUERY_DIR):
        # Ensuring that it is a video file.
        if filename.endswith(".mp4"):
            query_lst.append(QUERY_DIR + "/" + filename)

    return query_lst


if __name__ == '__main__':
    # Loading the Captioning Model.
    clip_caption_generator.init()

    relevance_2_lst, relevance_4_lst, relevance_8_lst, relevance_16_lst = [], [], [], []

    # Obtaining the list of videos
    query_lst = get_query_list()

    # Loading the ground truth
    with open(GROUND_TRUTH, 'rb') as handle:
        groundtruth = pickle.load(handle)

    # Iterating over the query files
    for query in query_lst:
        print("eval_qik.py :: Processing query :: ", query)

        try:
            # QIK Search on the video
            results = qik_search.qik_search(query)
            print("results :: ", results)

            # Obtaining the id list
            id_lst = []
            for result in results:
                # print("result :: ", result)
                # Obtaining the candidate id
                # id_lst.append(result[:-4]) # For LCS
                # id_lst.append(result[0][:-7]) # For number of matching scenes
                id_lst.append(result[0][:-4])


            # Removing the query from the result list.
            query_name = query.split("/")[-1]
            if query_name in id_lst:
                id_lst.remove(query_name)

            print("id_lst :: ", id_lst)
            # Writing results to the file
            with open(RESULTS_FILE_PREFIX + ".txt", 'a+') as f:
                f.write(query + "=" + str(id_lst) + "\n")

            # Obtaining the ground truth
            ground_truth = get_ground_truth(query.split("/")[-1][:-4], groundtruth)
            print("eval_qik :: ground_truth :: ", ground_truth)

            # Obtaining the relevance of the results
            relevance_2_lst.append(get_binary_relevance(id_lst[:2], ground_truth))
            relevance_4_lst.append(get_binary_relevance(id_lst[:4], ground_truth))
            relevance_8_lst.append(get_binary_relevance(id_lst[:8], ground_truth))
            relevance_16_lst.append(get_binary_relevance(id_lst[:16], ground_truth))
            print("eval_qik.py :: get_binary_relevance(id_lst, ground_truth) :: ", get_binary_relevance(id_lst, ground_truth))
        except Exception as e:
            print("eval_qik.py :: Exception occurred processing query :: ", query)
            traceback.print_exc()

    # Writing relevance lists
    with open(RESULTS_FILE_PREFIX + '_relevance_2_lst.pkl', 'wb') as fp:
        pickle.dump(relevance_2_lst, fp)
    with open(RESULTS_FILE_PREFIX + '_relevance_4_lst.pkl', 'wb') as fp:
        pickle.dump(relevance_4_lst, fp)
    with open(RESULTS_FILE_PREFIX + '_relevance_8_lst.pkl', 'wb') as fp:
        pickle.dump(relevance_8_lst, fp)
    with open(RESULTS_FILE_PREFIX + '_relevance_16_lst.pkl', 'wb') as fp:
        pickle.dump(relevance_16_lst, fp)

    # Obtaining the mAP for the results
    mAP_2 = get_mAP(relevance_2_lst)
    print("eval_qik.py :: mAP_2 :: ", mAP_2)
    mAP_4 = get_mAP(relevance_4_lst)
    print("eval_qik.py :: mAP_4 :: ", mAP_4)
    mAP_8 = get_mAP(relevance_8_lst)
    print("eval_qik.py :: mAP_8 :: ", mAP_8)
    mAP_16 = get_mAP(relevance_16_lst)
    print("eval_qik.py :: mAP_16 :: ", mAP_16)

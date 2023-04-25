# Imports
from sys import path
path.append("../QIK_Web/util")
path.append("../ML_Models/ShowAndTell/im2txt")

import os
import qik_search
import pickle
import traceback
import clip_caption_generator
import time
import datetime
import argparse
import numpy as np

# Constants/Configurations
QUERY_DIR = "/mydata/MSR_VTT/TestVideo"
GROUND_TRUTH = "data/Ground_Truth.pkl"
RESULTS_FILE_PREFIX = "data/qik_msrvtt_q_testset_d_trainvalset_results"
RANKING_FUNCTION = "ted_and_lcs"

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


def get_query_list(query_dir):
    query_lst = []

    # Iterating over the video directory
    for filename in os.listdir(query_dir):
        # Ensuring that it is a video file.
        if filename.endswith(".mp4"):
            query_lst.append(filename)

    return query_lst


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='QIK Evaluation')
    parser.add_argument('-query_dir', default=QUERY_DIR, metavar='data', help='Directory containing query videos', required=False)
    parser.add_argument('-ranking_func', default=RANKING_FUNCTION, metavar='data', help='The ranking scheme to use', required=False)
    parser.add_argument('-ground_truth', default=GROUND_TRUTH, metavar='data', help='Ground truth file', required=False)
    parser.add_argument('-results_prefix', default=RESULTS_FILE_PREFIX, metavar='data', help='Path and prefix to the results files', required=False)
    args = parser.parse_args()

    # Loading the Captioning Model.
    clip_caption_generator.init()

    relevance_2_lst, relevance_4_lst, relevance_8_lst, relevance_16_lst, ret_dict = [], [], [], [], {}

    # Obtaining the list of videos
    query_lst = get_query_list(args.query_dir)

    # Loading the ground truth
    with open(args.ground_truth, 'rb') as handle:
        groundtruth = pickle.load(handle)

    # Iterating over the query files
    for query in query_lst:
        print("eval_qik.py :: Processing query :: ", query)

        try:
            # Noting the time taken for further auditing.
            time = datetime.datetime.now()

            # QIK Search on the video
            results = qik_search.qik_search(args.query_dir + "/" + query, ranking_func=args.ranking_func)

            # Noting QIK time.
            qik_time = datetime.datetime.now() - time

            # Obtaining the id list
            id_lst = []
            for result in results:
                id_lst.append(result[0])

            # Removing the query from the result list.
            if query in id_lst:
                id_lst.remove(query)

            # Adding data to the return dictionary.
            ret_dict["qik_time"] = qik_time.total_seconds()
            ret_dict["qik_" + args.ranking_func + "_results"] = id_lst

            # Writing results to the file
            with open(args.results_prefix + ".txt", 'a+') as f:
                f.write(query + "=" + str(ret_dict) + "\n")

            # Obtaining the ground truth
            ground_truth = get_ground_truth(query, groundtruth)

            # Obtaining the relevance of the results
            relevance_2_lst.append(get_binary_relevance(id_lst[:2], ground_truth))
            relevance_4_lst.append(get_binary_relevance(id_lst[:4], ground_truth))
            relevance_8_lst.append(get_binary_relevance(id_lst[:8], ground_truth))
            relevance_16_lst.append(get_binary_relevance(id_lst[:16], ground_truth))
        except Exception as e:
            print("eval_qik.py :: Exception occurred processing query :: ", query)
            traceback.print_exc()

    # Obtaining the mAP for the results
    mAP_2 = get_mAP(relevance_2_lst)
    print("eval_qik.py :: mAP_2 :: ", mAP_2)
    mAP_4 = get_mAP(relevance_4_lst)
    print("eval_qik.py :: mAP_4 :: ", mAP_4)
    mAP_8 = get_mAP(relevance_8_lst)
    print("eval_qik.py :: mAP_8 :: ", mAP_8)
    mAP_16 = get_mAP(relevance_16_lst)
    print("eval_qik.py :: mAP_16 :: ", mAP_16)

import pickle
import json
import numpy as np
import argparse

# Constants/Configurations
RESULTS_FILE = "qik_msrvtt_q_testset_d_trainvalset_results_lcs.txt"
# RESULTS_FILE = "csq_msrvtt_results.txt"
GROUND_TRUTH = "MSRVTT_Regrouped_Categories_Ground_Truth_10_1.pkl"

# Ref: https://gist.github.com/bwhite/3726239 - Start
def precision_at_k(r, k):
    assert k >= 1
    r = np.asarray(r)[:k] != 0
    if r.size != k:
        raise ValueError('Relevance score length < k')
    return np.mean(r)

# Old way to compute
# def average_precision(r):
#     r = np.asarray(r) != 0
#     out = [precision_at_k(r, k + 1) for k in range(r.size) if r[k]]
#     if not out:
#         return 0.
#     return np.mean(out)

# New way to compute
def average_precision(r):
    r = np.asarray(r) != 0
    # out = [precision_at_k(r, k + 1) for k in range(r.size) if r[k]]
    out = []
    for k in range(r.size):
        if r[k]:
            out.append(precision_at_k(r, k + 1))
        else:
            out.append(0)
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


def get_match_count(res, ground_truth):
    count = 0
    for result in res:
        if result in ground_truth:
            count += 1
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to create the ground truth for the MSR-VTT dataset.")
    parser.add_argument('-results', default=RESULTS_FILE, metavar='data', help='Path to the obtained results file.', required=False)
    parser.add_argument('-groundtruth', default=GROUND_TRUTH, metavar='data', help='Path to the ground truth.', required=False)
    args = parser.parse_args()

    relevance_2_lst, relevance_4_lst, relevance_8_lst, relevance_16_lst = [], [], [], []

    # Load the ground truth
    with open(args.groundtruth, 'rb') as handle:
        groundtruth = pickle.load(handle)

    # Iterating over the results
    with open(args.results) as res_file:
        for line in res_file:
            splits = line.strip().split("=")
            file_name = splits[0].split("/")[-1][:-4]

            # Obtaining the results
            res = json.loads(splits[1].replace("'", "\"").replace(".mp4", ""))

            # Obtaining the ground truth for the respective image
            ground_truth = get_ground_truth(file_name, groundtruth)

            if len(res) < 16:
                print("QIK LCS results count is less than 16")
                continue
            count = get_match_count(res, ground_truth)


            print("compute_mAP_based_on_categories_input_video_to_skip.py :: file_name :: ", file_name, " :: res :: ", res)

            print("compute_mAP_based_on_categories_input_video_to_skip.py :: relevance (k = 2) :: ", get_binary_relevance(res[:2], ground_truth))
            print("compute_mAP_based_on_categories_input_video_to_skip.py :: relevance (k = 4) :: ", get_binary_relevance(res[:4], ground_truth))
            print("compute_mAP_based_on_categories_input_video_to_skip.py :: relevance (k = 8) :: ", get_binary_relevance(res[:8], ground_truth))
            print("compute_mAP_based_on_categories_input_video_to_skip.py :: relevance (k = 16) :: ", get_binary_relevance(res[:16], ground_truth))

            # Obtaining the relevance of the results
            relevance_2_lst.append(get_binary_relevance(res[:2], ground_truth))
            relevance_4_lst.append(get_binary_relevance(res[:4], ground_truth))
            relevance_8_lst.append(get_binary_relevance(res[:8], ground_truth))
            relevance_16_lst.append(get_binary_relevance(res[:16], ground_truth))

    # Obtaining the mAP for the results
    print("compute_mAP_based_on_categories_input_video_to_skip.py :: mAP@2: ", get_mAP(relevance_2_lst))
    print("compute_mAP_based_on_categories_input_video_to_skip.py :: mAP@4: ", get_mAP(relevance_4_lst))
    print("compute_mAP_based_on_categories_input_video_to_skip.py :: mAP@8: ", get_mAP(relevance_8_lst))
    print("compute_mAP_based_on_categories_input_video_to_skip.py :: mAP@16: ", get_mAP(relevance_16_lst))

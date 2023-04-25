import pickle
import json
import numpy as np
import pandas as pd

# Constants/Configurations
RESULTS_FILE = "qik_svw_test_set_results.txt"
GROUND_TRUTH = "SVW_Ground_Truth.pkl"
ANN_FILE = "SVW.csv"
MAP_FILTERED_RESULTS_FILE = "qik_svw_test_set_results_filtered.txt"

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


def get_testset_videos():
    ret_lst = []
    df = pd.read_csv(ANN_FILE)
    for index, row in df.iterrows():
        if not pd.isnull(row['FileName']):
            if row['Train 1?'] == 0:
                ret_lst.append(row['FileName'][:-4])
    return ret_lst


if __name__ == "__main__":
    relevance_2_lst, relevance_4_lst, relevance_8_lst, relevance_16_lst = [], [], [], []

    # Load the ground truth
    with open(GROUND_TRUTH, 'rb') as handle:
        groundtruth = pickle.load(handle)

    # Obtaining the test set videos
    testset_videos = get_testset_videos()

    # Iterating over the results
    with open(RESULTS_FILE) as res_file:
        for line in res_file:
            splits = line.strip().split("=")
            file_name = splits[0].split("/")[-1][:-4]

            # Ensure that we are using only the testset videos
            if file_name not in testset_videos:
                continue

            # Obtaining the results
            res = json.loads(splits[1].replace("'", "\"").replace(".mp4", ""))
            print("eval_qik.py :: Results :: file_name :: ", file_name, " :: res :: ", res)

            # Filtering training set results from the test set
            for res_file in res:
                if res_file not in testset_videos:
                    res.remove(res_file)
            print("eval_qik.py :: Filtered Results :: file_name :: ", file_name, " :: res :: ", res)

            # Writing results to the file
            with open(MAP_FILTERED_RESULTS_FILE + ".txt", 'a+') as f:
                f.write(file_name + "=" + str(res_file) + "\n")

            # Obtaining the ground truth
            ground_truth = get_ground_truth(file_name, groundtruth)
            print("eval_qik :: ground_truth :: ", ground_truth)

            # Skipping queries for which there was no ground truth
            if not ground_truth:
                continue

            # Obtaining the relevance of the results
            relevance_2 = get_binary_relevance(res[:2], ground_truth)
            relevance_4 = get_binary_relevance(res[:4], ground_truth)
            relevance_8 = get_binary_relevance(res[:8], ground_truth)
            relevance_16 = get_binary_relevance(res[:16], ground_truth)

            print("eval_qik.py :: relevance (k = 2) :: ", relevance_2)
            print("eval_qik.py :: relevance (k = 4) :: ", relevance_4)
            print("eval_qik.py :: relevance (k = 8) :: ", relevance_8)
            print("eval_qik.py :: relevance (k = 16) :: ", relevance_16)

            # Adding to the relevance lists
            relevance_2_lst.append(relevance_2)
            relevance_4_lst.append(relevance_4)
            relevance_8_lst.append(relevance_8)
            relevance_16_lst.append(relevance_16)

    # Obtaining the mAP for the results
    print("eval_qik.py :: mAP@2: ", get_mAP(relevance_2_lst))
    print("eval_qik.py :: mAP@4: ", get_mAP(relevance_4_lst))
    print("eval_qik.py :: mAP@8: ", get_mAP(relevance_8_lst))
    print("eval_qik.py :: mAP@16: ", get_mAP(relevance_16_lst))

import pickle
import argparse
import numpy as np
from prettytable import PrettyTable

# Ref: https://gist.github.com/bwhite/3726239 - Start
def precision_at_k(r, k):
    assert k >= 1
    r = np.asarray(r)[:k] != 0
    if r.size != k:
        raise ValueError('Relevance score length < k')
    return np.mean(r)

# Old way to compute
def average_precision(r):
    r = np.asarray(r) != 0
    out = [precision_at_k(r, k + 1) for k in range(r.size) if r[k]]
    if not out:
        return 0.
    return np.mean(out)

def mean_average_precision(rs):
    return np.mean([average_precision(r) for r in rs])
# Ref: https://gist.github.com/bwhite/3726239 - End

# Function to get the average for a list.
def get_average(results):
    if len(results) == 0:
        return 0
    total_average = 0

    for average in results:
        total_average += average

    mean_average = total_average / len(results)
    return mean_average

def get_mAP(results):
    return mean_average_precision(results)

def get_binary_relevance(results, ground_truth):
    relevance_results = [1 if result in ground_truth else 0 for result in results]
    return relevance_results

def get_pickle_data(file):
    with open(file, 'rb') as handle:
        data = pickle.load(handle)
    return data

def get_query_lst(query_lst):
    ret_lst = []
    with open(query_lst, "r") as file:
        for video in file:
            ret_lst.append(video)
    return ret_lst

def get_ground_truth(video_id, groundtruth):
    for key in groundtruth:
        if video_id in groundtruth[key]:
            return groundtruth[key]

def get_mAP_Values(query_lst, pre_computed_results, technique, ground_truth):
    # Intializing the lists
    k_2_mean_relevance_lst, k_4_mean_relevance_lst, k_8_mean_relevance_lst, k_16_mean_relevance_lst, time_lst = [], [], [], [], []

    # Iterating over the query videos.
    for video in query_lst:
        # Obtaining the results
        results = pre_computed_results[video.rstrip()][technique + "_results"]
        time = pre_computed_results[video.rstrip()][technique + "_time"]

        # Obtaining the ground truth
        video_ground_truth = get_ground_truth(video.rstrip(), ground_truth)

        # Obtaining the relevance results
        k_2_mean_relevance_lst.append(get_binary_relevance(results[:2], video_ground_truth))
        k_4_mean_relevance_lst.append(get_binary_relevance(results[:4], video_ground_truth))
        k_8_mean_relevance_lst.append(get_binary_relevance(results[:8], video_ground_truth))
        k_16_mean_relevance_lst.append(get_binary_relevance(results[:16], video_ground_truth))
        time_lst.append(time)

    # Computing the mAP scores 
    mAP_2 = get_mAP(k_2_mean_relevance_lst)
    mAP_4 = get_mAP(k_4_mean_relevance_lst)
    mAP_8 = get_mAP(k_8_mean_relevance_lst)
    mAP_16 = get_mAP(k_16_mean_relevance_lst)
    time_avg = get_average(time_lst)

    return mAP_2, mAP_4, mAP_8, mAP_16, time_avg

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compute MAP for pre-fetched query results.')
    parser.add_argument('-video_data', default="data/MSR_VTT_Query_Files.txt", metavar='data', help='File containing the list of videos', required=False)
    parser.add_argument('-pre_computed_results', default="pre_constructed_data/Video_Retrieval_Results.pkl", help='Pre-fetched results file path', required=False)
    parser.add_argument('-ground_truth', default="data/Ground_Truth.pkl", help='Pre-constructed ground truth', required=False)
    args = parser.parse_args()

    query_lst = get_query_lst(args.video_data)
    ground_truth = get_pickle_data(args.ground_truth)
    pre_computed_results = get_pickle_data(args.pre_computed_results)

    qik_scene_match_mAP_2, qik_scene_match_mAP_4, qik_scene_match_mAP_8, qik_scene_match_mAP_16, qik_scene_match_avg_time = get_mAP_Values(query_lst, pre_computed_results, "qik_scene_match", ground_truth)
    qik_lcs_mAP_2, qik_lcs_mAP_4, qik_lcs_mAP_8, qik_lcs_mAP_16, qik_lcs_avg_time = get_mAP_Values(query_lst, pre_computed_results, "qik_lcs", ground_truth)
    qik_ted_and_lcs_mAP_2, qik_ted_and_lcs_mAP_4, qik_ted_and_lcs_mAP_8, qik_ted_and_lcs_mAP_16, qik_ted_and_lcs_avg_time = get_mAP_Values(query_lst, pre_computed_results, "qik_ted_and_lcs", ground_truth)
    qik_scene_match_ted_and_lcs_mAP_2, qik_scene_match_ted_and_lcs_mAP_4, qik_scene_match_ted_and_lcs_mAP_8, qik_scene_match_ted_and_lcs_mAP_16, qik_scene_match_ted_and_lcs_avg_time = get_mAP_Values(query_lst, pre_computed_results, "qik_scene_match_ted_and_lcs", ground_truth)
    dns_1_mAP_2, dns_1_mAP_4, dns_1_mAP_8, dns_1_mAP_16, dns_1_avg_time = get_mAP_Values(query_lst, pre_computed_results, "dns_1", ground_truth)
    dns_0_mAP_2, dns_0_mAP_4, dns_0_mAP_8, dns_0_mAP_16, dns_0_avg_time = get_mAP_Values(query_lst, pre_computed_results, "dns_0", ground_truth)
    dns_0_5_mAP_2, dns_0_5_mAP_4, dns_0_5_mAP_8, dns_0_5_mAP_16, dns_0_5_avg_time = get_mAP_Values(query_lst, pre_computed_results, "dns_0.5", ground_truth)
    csq_mAP_2, csq_mAP_4, csq_mAP_8, csq_mAP_16, csq_avg_time = get_mAP_Values(query_lst, pre_computed_results, "csq", ground_truth)

    # Pretty printing the results.
    t = PrettyTable(['System', 'k=2', 'k=4', 'k=8', 'k=16', "Average Time(s)"])
    t.add_row(['QIK (Scene Match)', round(qik_scene_match_mAP_2, 4), round(qik_scene_match_mAP_4, 4), round(qik_scene_match_mAP_8, 4), round(qik_scene_match_mAP_16, 4), round(qik_scene_match_avg_time, 4)])
    t.add_row(['QIK (LCS)', round(qik_lcs_mAP_2, 4), round(qik_lcs_mAP_4, 4), round(qik_lcs_mAP_8, 4), round(qik_lcs_mAP_16, 4), round(qik_lcs_avg_time, 4)])
    t.add_row(['QIK (LCS and TED)', round(qik_ted_and_lcs_mAP_2, 4), round(qik_ted_and_lcs_mAP_4, 4), round(qik_ted_and_lcs_mAP_8, 4), round(qik_ted_and_lcs_mAP_16, 4), round(qik_ted_and_lcs_avg_time, 4)])
    t.add_row(['QIK (Scene Match, LCS and TED)', round(qik_scene_match_ted_and_lcs_mAP_2, 4), round(qik_scene_match_ted_and_lcs_mAP_4, 4), round(qik_scene_match_ted_and_lcs_mAP_8, 4), round(qik_scene_match_ted_and_lcs_mAP_16, 4), round(qik_scene_match_ted_and_lcs_avg_time, 4)])
    t.add_row(['DnS (%=1)', round(dns_1_mAP_2, 4), round(dns_1_mAP_4, 4), round(dns_1_mAP_8, 4), round(dns_1_mAP_16, 4), round(dns_1_avg_time, 4)])
    t.add_row(['DnS (%=0)', round(dns_0_mAP_2, 4), round(dns_0_mAP_4, 4), round(dns_0_mAP_8, 4), round(dns_0_mAP_16, 4), round(dns_0_avg_time, 4)])
    t.add_row(['DnS (%=0.5)', round(dns_0_5_mAP_2, 4), round(dns_0_5_mAP_4, 4), round(dns_0_5_mAP_8, 4), round(dns_0_5_mAP_16, 4), round(dns_0_5_avg_time, 4)])
    t.add_row(['CSQ', round(csq_mAP_2, 4), round(csq_mAP_4, 4), round(csq_mAP_8, 4), round(csq_mAP_16, 4), round(csq_avg_time, 4)])
    print(t)
    print("Total no of queries considered = ", len(query_lst))

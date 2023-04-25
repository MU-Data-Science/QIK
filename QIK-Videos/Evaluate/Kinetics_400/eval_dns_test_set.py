# Imports
from sys import path
path.append("../distill-and-select")

import torch
import pickle
import os.path
import numpy as np
from model.feature_extractor import FeatureExtractor
from model.students import FineGrainedStudent, CoarseGrainedStudent
from model.selector import SelectorNetwork
from utils import load_video, collate_eval

# Configurations
PERCENTAGE = 0.75 # Percentage for re-ranking
TARGET_DIR = "/mydata/Kinetics_Video_Test_Set_Data_Trimmed"
QUERY_DIR = "/mydata/Kinetics_Query_Set_Trimmed"
FEATURE_DIR = "/mydata/Kinetics_Trimmed_Feature_Data"

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
    for key in groundtruth:
        if video_id in groundtruth[key]:
            return groundtruth[key]


def get_video_list(inp_dir):
    video_lst = []

    # Iterating over the video directory
    for filename in os.listdir(inp_dir):
        # Ensuring that it is a video file.
        if filename.endswith(".mp4"):
            video_lst.append(filename)

    return video_lst


if __name__ == '__main__':
    relevance_2_lst, relevance_4_lst, relevance_8_lst, relevance_16_lst = [], [], [], []

    # Creating features directory if it does not exist
    os.makedirs(FEATURE_DIR, exist_ok=True)

    # Obtaining the list of videos
    target_lst = get_video_list(TARGET_DIR)
    query_lst = get_video_list(QUERY_DIR)

    # Feature extraction network used in the experiments
    feature_extractor = FeatureExtractor(dims=512)

    # Fine-grained Students
    fg_att_student = FineGrainedStudent(pretrained=True, attention=True)
    fg_bin_student = FineGrainedStudent(pretrained=True, binarization=True)

    # Coarse-grained Students
    cg_student = CoarseGrainedStudent(pretrained=True)

    # Selector Networks
    selector_att = SelectorNetwork(pretrained=True, attention=True)
    selector_bin = SelectorNetwork(pretrained=True, binarization=True)

    # Setting the model in evalution mode
    selector_att.eval()

    # Loading the ground truth
    with open('kinetics400_groundtruth.pickle', 'rb') as handle:
        groundtruth = pickle.load(handle)

    # Iterating over the query
    for query in query_lst:
        print("eval_dns_test_set.py :: processing query :: ", query)

        try:
            # Check if video features are present
            if not os.path.isfile(FEATURE_DIR + "/" + query + ".pickle"):
                # Extracting query features
                print("eval_dns_test_set.py :: Extracting query features for the query :: ", query)
                query_video = torch.from_numpy(load_video(QUERY_DIR + "/" + query, cc_size=224, rs_size=256))
                video_features = feature_extractor(query_video)
                max_len = video_features.size(0)
                max_reg = video_features.size(1)
                padded_videos = video_features.new(*(1, max_len, max_reg, 512)).fill_(0)
                length = video_features.size(0)
                padded_videos[0, :length] = video_features

                # Saving the features as a pickle file
                with open(FEATURE_DIR + "/" + query + ".pickle", 'wb') as f:
                    pickle.dump(padded_videos, f)

            # Load preconstructed features
            with open(FEATURE_DIR + "/" + query + ".pickle", 'rb') as f:
                padded_videos = pickle.load(f)

                # Extracting query video representations for the student and selector networks
                query_fg_features = fg_att_student.index_video(padded_videos)
                query_cg_features = cg_student.index_video(padded_videos)
                query_sn_features = selector_att.index_video(padded_videos)

                similarity_lst, result_lst = [], []
                # Iterating over the target
                for targ in target_lst:

                    # Skipping the query video
                    if targ == query:
                        continue

                    try:
                        # Check if video features are present
                        if not os.path.isfile(FEATURE_DIR + "/" + targ + ".pickle"):
                            # Extracting the video features
                            print("eval_dns_test_set.py :: Extracting query features for the targ :: ", targ)
                            targ_video = torch.from_numpy(load_video(TARGET_DIR + "/" + targ, cc_size=224, rs_size=256))
                            video_features = feature_extractor(targ_video)
                            max_len = video_features.size(0)
                            max_reg = video_features.size(1)
                            padded_videos = video_features.new(*(1, max_len, max_reg, 512)).fill_(0)
                            length = video_features.size(0)
                            padded_videos[0, :length] = video_features

                            # Saving the features as a pickle file
                            with open(FEATURE_DIR + "/" + targ + ".pickle", 'wb') as f:
                                pickle.dump(padded_videos, f)

                        # Load preconstructed features
                        with open(FEATURE_DIR + "/" + targ + ".pickle", 'rb') as f:
                            padded_videos = pickle.load(f)

                            # Extracting coarse grained features
                            cg_features = cg_student.index_video(padded_videos)

                            # Obtaining selector features
                            sn_features = selector_att.index_video(padded_videos)

                            # Obtaining the coarse grained similarity
                            coarse_similarity = cg_student.calculate_video_similarity(query_cg_features, cg_features)

                            # Obtaining the selector scores
                            selector_features = torch.cat([query_sn_features, sn_features, coarse_similarity], 1)
                            selector_scores = selector_att(selector_features).squeeze(-1).detach().numpy()[0]
                            similarity_lst.append(selector_scores)

                    except:
                        print("eval_dns_test_set.py :: Exception occurred processing targ :: ", targ)

                # Ranking the results based on the coarse grained selector scores
                ranked_selector_scores_lst = np.argsort(np.array(similarity_lst))[::-1][:len(similarity_lst)]

                # Obtaining a percentage of the results for re-ranking
                percent_ranked_selector_scores_lst = ranked_selector_scores_lst[
                                                     :int(PERCENTAGE * len(ranked_selector_scores_lst))]

                print("eval_dns_test_set.py :: Re-ranking the results for query :: ", query)
                # Re-ranking the results
                if len(percent_ranked_selector_scores_lst):
                    for idx in percent_ranked_selector_scores_lst:
                        targ = target_lst[idx]

                        # Check if video features are present
                        if not os.path.isfile(FEATURE_DIR + "/" + targ + ".pickle"):
                            print("eval_dns_test_set.py :: Pre-constructed features not available while ranking. Skipping for raking for targ :: ", targ)
                            continue

                        try:
                            # Load preconstructed features
                            with open(FEATURE_DIR + "/" + targ + ".pickle", 'rb') as f:
                                padded_videos = pickle.load(f)

                                # Extracting fine grained features
                                fg_features = fg_att_student.index_video(padded_videos)

                                # Obtaining the fine grained similarity
                                fine_similarity = fg_att_student.calculate_video_similarity(query_fg_features, fg_features)
                                fine_similarity = fine_similarity.squeeze(-1).detach().numpy()[0]

                                # Updating the similarity scores with the fine grained scores
                                similarity_lst[idx] = fine_similarity
                        except:
                            print("eval_dns_test_set.py :: Exception occurred re-ranking targ :: ", targ)

                # Obtaining the final ranked results
                ranked_selector_scores_lst = np.argsort(np.array(similarity_lst))[::-1][:len(similarity_lst)]

                # Obtaining the ground truth
                ground_truth = get_ground_truth(query.split("/")[-1], groundtruth)

                # Creating a result list based on the index
                for idx in ranked_selector_scores_lst:
                    result_lst.append(target_lst[idx].split("/")[-1])

                # Obtaining the relevance of the results
                relevance_2_lst.append(get_binary_relevance(result_lst[:2], ground_truth))
                relevance_4_lst.append(get_binary_relevance(result_lst[:4], ground_truth))
                relevance_8_lst.append(get_binary_relevance(result_lst[:8], ground_truth))
                relevance_16_lst.append(get_binary_relevance(result_lst[:16], ground_truth))

        except Exception as e:
            print("eval_dns_test_set.py :: Exception occurred processing query :: ", query)
            print("eval_dns_test_set.py :: Exception :: " + str(e))

    # Writing relevalnce lists
    with open('dns_relevance_2_lst.pkl', 'wb') as fp:
        pickle.dump(relevance_2_lst, fp)
    with open('dns_relevance_4_lst.pkl', 'wb') as fp:
        pickle.dump(relevance_4_lst, fp)
    with open('dns_relevance_8_lst.pkl', 'wb') as fp:
        pickle.dump(relevance_8_lst, fp)
    with open('dns_relevance_16_lst.pkl', 'wb') as fp:
        pickle.dump(relevance_16_lst, fp)

    # Obtaining the mAP for the results
    mAP_2 = get_mAP(relevance_2_lst)
    print("mAP_2 :: ", mAP_2)
    mAP_4 = get_mAP(relevance_4_lst)
    print("mAP_4 :: ", mAP_4)
    mAP_8 = get_mAP(relevance_8_lst)
    print("mAP_8 :: ", mAP_8)
    mAP_16 = get_mAP(relevance_16_lst)
    print("mAP_16 :: ", mAP_16)
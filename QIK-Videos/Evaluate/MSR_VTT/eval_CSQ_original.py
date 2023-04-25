# Imports
from sys import path
path.append("../Hadamard-Matrix-for-hashing")

import torch
import cv2
import os
import pickle
import datetime
import numpy as np
import video.data.video_transforms as transforms
import video.data.video_sampler as sampler
from video.network.symbol_builder import get_symbol


# Constants
DATABASE_DIR = "/mydata/MSR_VTT/TrainValVideo"
QUERY_DIR = "/mydata/MSR_VTT/TestVideo"
GROUND_TRUTH_FILE = "MSRVTT_All_Data_Categories_Ground_Truth.pkl"


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


def get_binary_relevance(results, ground_truth):
    relevance_results = [1 if result in ground_truth else 0 for result in results]
    return relevance_results


def get_mAP(results):
    return mean_average_precision(results)


def get_ground_truth(video_id, groundtruth):
    for key in groundtruth:
        if video_id in groundtruth[key]:
            return groundtruth[key]


# To obtain features from a video
def extract_frames_fast(cap, idxs, force_color=True):
        if len(idxs) < 1:
            return []

        frames = []
        pre_idx = max(idxs)
        for idx in idxs:
            if pre_idx != (idx - 1):
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            res, frame = cap.read() # in BGR/GRAY format
            pre_idx = idx
            if not res:
                faulty_frame = idx
                return None
            if len(frame.shape) < 3:
                if force_color:
                    # Convert Gray to RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            else:
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame)
        return frames


def extract_frames_slow(cap, idxs, force_color=True):
    if len(idxs) < 1:
        return []

    frames = [None] * len(idxs)
    idx = min(idxs)
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    while idx <= max(idxs):
        res, frame = cap.read()  # in BGR/GRAY format
        if not res:
            # end of the video
            faulty_frame = idx
            return None
        if idx in idxs:
            # fond a frame
            if len(frame.shape) < 3:
                if force_color:
                    # Convert Gray to RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            else:
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pos = [k for k, i in enumerate(idxs) if i == idx]
            for k in pos:
                frames[k] = frame
        idx += 1
    return frames


def extract_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    val_sampler = sampler.SequentialSampling(num=16,
                                             interval=2,
                                             fix_cursor=True,
                                             shuffle=True)

    sampled_idxs = val_sampler.sampling(range_max=frame_count, v_id=None, prev_failed=None)
    sampled_frames = extract_frames_fast(cap, sampled_idxs, True)
    if sampled_frames is None:
        # try slow method:
        sampled_frames = extract_frames_slow(cap, sampled_idxs, True)
    clip_input = np.concatenate(sampled_frames, axis=2)
    clip_input = video_transform(clip_input)
    clip_input = clip_input[None, :, :]
    return clip_input


# To obtain the hash code
def predict_hash_code(model, input):
    model.eval()
    input = input.float()
    y = model(input)
    output = y.data.cpu().float()
    return output


def convert_list(db_lst):
    is_start = True
    for db in db_lst:
        if is_start:
            all_output = db
            is_start = False
        else:
            all_output = torch.cat((all_output, db), 0)
    return all_output.cpu().numpy()


if __name__ == '__main__':
    net, input_conf = get_symbol(name="MFNet_3D", pretrained=True, print_net=False, hash_bit=64, )
    net.eval()
    net = torch.nn.DataParallel(net)

    # Loading the pre-trained model
    checkpoint = torch.load("video_ep-0100_MSR_VTT_64bits.pth", map_location=torch.device('cpu'))
    net.load_state_dict(checkpoint['state_dict'])

    # Loading the ground truth
    with open(GROUND_TRUTH_FILE, 'rb') as handle:
        groundtruth = pickle.load(handle)

    # For video augmentation
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

    video_transform = transforms.Compose([transforms.Resize((256, 256)),
                                          transforms.CenterCrop((224, 224)),
                                          transforms.ToTensor(),
                                          normalize,
                                          ])

    # Intializing the database hash list
    database_hash_lst = []
    query_hash_lst = []
    database_file_lst = []
    result_dict = {}

    # Initializing an array to hold all relevance results.
    relevance_2_lst, relevance_4_lst, relevance_8_lst, relevance_16_lst, relevance_100_lst = [], [], [], [], []

    # Iterating over the database videos
    for filename in os.listdir(DATABASE_DIR):
        # Obtaining the features of the input video
        try:
            database_hash = predict_hash_code(net, extract_frames(DATABASE_DIR + "/" + filename))
            database_hash_lst.append(database_hash)
            database_file_lst.append(filename)
        except:
            print("eval_CSQ.py :: Skipping file : ", filename)


    # Iterating over the query videos
    for filename in os.listdir(QUERY_DIR):
        # Obtaining the features of the input video
        try:
            # Noting the time taken for further auditing.
            start_time = datetime.datetime.now()

            query_hash_lst = []
            query_hash = predict_hash_code(net, extract_frames(QUERY_DIR + "/" + filename))
            query_hash_lst.append(query_hash)

            # Converting from a list
            db = convert_list(database_hash_lst)
            queries = convert_list(query_hash_lst)

            # Computing the similarity
            sim = np.dot(db, queries.T)
            ids = np.argsort(-sim, axis=0)

            # Obtaining the ids
            idx = ids[:, 0]

            # Initializing an array to hold the search results
            result_lst = []

            # Iterating over the ids
            for id in idx:
                result_lst.append(database_file_lst[id])

            csq_retrieval_time = datetime.datetime.now()
            result_dict['csqRetrievalTime'] = (csq_retrieval_time - start_time).total_seconds()

            # Removing the query from the result list.
            if filename in result_lst:
                result_lst.remove(filename)

            if not result_lst:
                print("eval_CSQ.py :: Results are empty for file : ", filename)

            result_dict['csqResults'] = result_lst[:100]

            # Writing results to the file
            with open('csq_msrvtt_results.txt', 'a+') as f:
                f.write(filename + "=" + str(result_dict) + "\n")

            # Obtaining the ground truth
            ground_truth = get_ground_truth(filename, groundtruth)

            if not ground_truth:
                print("eval_CSQ.py :: Ground truth is not present for the file : ", filename)
                continue

            # Obtaining result relevance
            relevance_2_lst.append(get_binary_relevance(result_lst[:2], ground_truth))
            relevance_4_lst.append(get_binary_relevance(result_lst[:4], ground_truth))
            relevance_8_lst.append(get_binary_relevance(result_lst[:8], ground_truth))
            relevance_16_lst.append(get_binary_relevance(result_lst[:16], ground_truth))
            relevance_100_lst.append(get_binary_relevance(result_lst[:100], ground_truth))

        except:
            print("eval_CSQ.py :: Skipping file : ", filename)

    print("mAP@2:", get_mAP(relevance_2_lst))
    print("mAP@4:", get_mAP(relevance_4_lst))
    print("mAP@8:", get_mAP(relevance_8_lst))
    print("mAP@16:", get_mAP(relevance_16_lst))
    print("mAP@100:", get_mAP(relevance_100_lst))


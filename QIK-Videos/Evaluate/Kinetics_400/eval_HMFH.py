# Imports
from sys import path
path.append("../Hadamard-Matrix-for-hashing")

import torch
import cv2
import os
import pickle
import numpy as np
import video.data.video_transforms as transforms
import video.data.video_sampler as sampler
from video.network.symbol_builder import get_symbol


# Constants
DATABASE_DIR = "/mydata/Kinetics_Subset"
GROUND_TRUTH_FILE = "kinetics400_groundtruth.pickle"

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
        assert cap is not None, "No opened video."
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


def extract_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    sampled_idxs = val_sampler.sampling(range_max=frame_count, v_id=None, prev_failed=None)
    sampled_frames = extract_frames_fast(cap, sampled_idxs, True)
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
    checkpoint = torch.load("64bit_87.38_PyTorch-MFNet-master.pth", map_location=torch.device('cpu'))
    net.load_state_dict(checkpoint['state_dict'])

    # For video augmentation
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

    video_transform = transforms.Compose([transforms.Resize((256, 256)),
                                          transforms.CenterCrop((224, 224)),
                                          transforms.ToTensor(),
                                          normalize,
                                          ])

    val_sampler = sampler.SequentialSampling(num=16,
                                             interval=2,
                                             fix_cursor=True,
                                             shuffle=True)

    # Intializing the database hash list
    database_hash_lst = []
    file_lst = []

    # Iterating over the videos
    for filename in os.listdir(DATABASE_DIR):
        # Obtaining the features of the input video
        try:
            database_hash = predict_hash_code(net, extract_frames(DATABASE_DIR + "/" + filename))
            database_hash_lst.append(database_hash)
            file_lst.append(filename)
        except:
            print("eval_HMFH.py :: Skipping file : ", filename)

    db = convert_list(database_hash_lst)

    # Computing the similarity
    sim = np.dot(db, db.T)
    ids = np.argsort(-sim, axis=0)

    # Obtaining the ground truth
    with open(GROUND_TRUTH_FILE, 'rb') as handle:
        groundtruth = pickle.load(handle)

    # Initializing an array to hold all relevance results.
    relevance_2_lst, relevance_4_lst, relevance_8_lst, relevance_16_lst = [], [], [], []

    # Iterating over the hashes.
    for i in range(len(ids)):
        # Obtaining the ids
        idx = ids[:, i]

        # Initializing an array to hold the search results
        result_lst = []

        # Iterating over the ids
        for id in idx:
            result_lst.append(file_lst[id])

        # Removing the query from the result list.
        result_lst.remove(file_lst[i])

        # Obtaining the ground truth
        ground_truth = get_ground_truth(file_lst[i], groundtruth)

        # Obtaining result relevance
        relevance_2_lst.append(get_binary_relevance(result_lst[:2], ground_truth))
        relevance_4_lst.append(get_binary_relevance(result_lst[:4], ground_truth))
        relevance_8_lst.append(get_binary_relevance(result_lst[:8], ground_truth))
        relevance_16_lst.append(get_binary_relevance(result_lst[:16], ground_truth))

    print("mAP_2 :: ", get_mAP(relevance_2_lst))
    print("mAP_4 :: ", get_mAP(relevance_4_lst))
    print("mAP_8 :: ", get_mAP(relevance_8_lst))
    print("mAP_16 :: ", get_mAP(relevance_16_lst))


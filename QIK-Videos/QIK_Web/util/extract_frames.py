# Ref:
# 1) https://github.com/monkeyDemon/AI-Toolbox/blob/master/preprocess%20ToolBox/keyframes_extract_tool/keyframes_extract_diff.py
# 2) https://www.codetd.com/en/article/8918629

import cv2
import numpy as np
from scipy.signal import argrelextrema

SMOOTHING_WINDOW_SIZE = 50


def smooth(x, window_len=13, window='hanning'):
    s = np.r_[2 * x[0] - x[window_len:1:-1],
              x, 2 * x[-1] - x[-1:-window_len:-1]]

    if window == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = getattr(np, window)(window_len)
    y = np.convolve(w / w.sum(), s, mode='same')
    return y[window_len - 1:-window_len + 1]


class Frame:
    def __init__(self, id, diff):
        self.id = id
        self.diff = diff

    def __lt__(self, other):
        if self.id == other.id:
            return self.id < other.id
        return self.id < other.id

    def __gt__(self, other):
        return other.__lt__(self)

    def __eq__(self, other):
        return self.id == other.id and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)


def rel_change(a, b):
    x = (b - a) / max(a, b)
    print(x)
    return x


def extract_key_scenes(video_path, dest_dir):
    # load video and compute diff between frames
    cap = cv2.VideoCapture(str(video_path))
    out_suffix = video_path.split("/")[-1].split(".")[0]
    curr_frame = None
    prev_frame = None
    frame_diffs = []
    frames = []
    success, frame = cap.read()
    i = 0
    while (success):
        luv = cv2.cvtColor(frame, cv2.COLOR_BGR2LUV)
        curr_frame = luv
        if curr_frame is not None and prev_frame is not None:
            diff = cv2.absdiff(curr_frame, prev_frame)
            diff_sum = np.sum(diff)
            diff_sum_mean = diff_sum / (diff.shape[0] * diff.shape[1])
            frame_diffs.append(diff_sum_mean)
            frame = Frame(i, diff_sum_mean)
            frames.append(frame)
        prev_frame = curr_frame
        i = i + 1
        success, frame = cap.read()
    cap.release()

    # compute keyframe
    keyframe_id_set = set()
    diff_array = np.array(frame_diffs)
    sm_diff_array = smooth(diff_array, SMOOTHING_WINDOW_SIZE)
    frame_indexes = np.asarray(argrelextrema(sm_diff_array, np.greater))[0]
    for i in frame_indexes:
        keyframe_id_set.add(frames[i - 1].id)

    # save all keyframes as image
    cap = cv2.VideoCapture(str(video_path))
    curr_frame = None
    keyframes = []
    success, frame = cap.read()
    idx = 0
    while (success):
        if idx in keyframe_id_set:
            name = out_suffix + "_keyframe_" + str(idx) + ".jpg"
            cv2.imwrite(dest_dir + "/" + name, frame)
            keyframe_id_set.remove(idx)
        idx = idx + 1
        success, frame = cap.read()
    cap.release()


if __name__ == '__main__':
    extract_key_scenes("/mydata/UCF_Testset/v_BandMarching_g04_c03.avi", "/mydata/Image_Dir")
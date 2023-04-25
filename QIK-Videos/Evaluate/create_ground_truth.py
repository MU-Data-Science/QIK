import argparse
import json
import pickle

ANN_FILES = ["test_videodatainfo.json", "train_val_videodatainfo.json"]

def create_ground_truth(ann_dir, out_file):
    # Initializing the ground truth dictionary
    ground_truth_dict = {}

    # Reading the annotations
    for ann in ANN_FILES:
        with open(ann_dir + "/" + ann) as file:
            data = json.load(file)

            # Obtaining all the videos
            videos = data["videos"]

            # Iterating over the videos
            for video in videos:
                video_id = video["video_id"] + ".mp4"
                video_category = video["category"]

                # Creating the ground truth based on the category
                if video_category in ground_truth_dict:
                    lst = ground_truth_dict[video_category]
                    lst.append(video_id)
                    ground_truth_dict[video_category] = lst
                else:
                    ground_truth_dict[video_category] = [video_id]

    # Creating the pickle file of the ground truth.
    with open(out_file, "wb+") as f:
        pickle.dump(ground_truth_dict, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Preprocess to compute the ground truth')
    parser.add_argument('-ann_dir', default="data", metavar='data', help='Directory hold MSR-VTT annotations', required=False)
    parser.add_argument('-out', default="data/Ground_Truth.pkl", metavar='data', help='Directory to write the ground truth.', required=False)
    args = parser.parse_args()

    create_ground_truth(args.ann_dir, args.out)
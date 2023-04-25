# Imports
import json
import pickle

# Constants
ANN_FILES = ["/mydata/MSR_VTT/test_videodatainfo.json", "/mydata/MSR_VTT/train_val_videodatainfo.json"]

if __name__ == '__main__':
    # Initializing the ground truth dictionary
    ground_truth_dict = {}

    # Reading the annotations
    for ann in ANN_FILES:
        with open(ann) as file:
            data = json.load(file)

            # Obtaining all the videos
            videos = data["videos"]

            # Iterating over the videos
            for video in videos:
                video_id = video["video_id"]
                video_category = video["category"]

                # Creating the ground truth based on the category
                if video_category in ground_truth_dict:
                    lst = ground_truth_dict[video_category]
                    lst.append(video_id)
                    ground_truth_dict[video_category] = lst
                else:
                    ground_truth_dict[video_category] = [video_id]

    # Creating the pickle file of the ground truth.
    with open("MSRVTT_All_Data_Categories_Ground_Truth.pkl", "wb") as f:
        pickle.dump(ground_truth_dict, f)



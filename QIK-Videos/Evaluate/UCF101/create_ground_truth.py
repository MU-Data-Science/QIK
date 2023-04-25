# Imports
import os
import pickle

# Configurations
VIDEO_DIR = "/mydata/UCF101"

if __name__ == "__main__":
    # Initializing map for holding categories and the corresponding videos.
    data_map = {}

    # Iterating over the files in the directory - k=2
    for file in os.listdir(os.fsencode(VIDEO_DIR)):
        filename = os.fsdecode(file)

        # Obtaining the category
        category = filename.split("_")[1]

        # Adding to the map
        if category in data_map:
            lst = data_map[category]
            lst.append(filename)
            data_map[category] = lst
        else:
            data_map[category] = [filename]

    # Saving the ground truth as a pickle file
    with open("ucf101_groundtruth.pickle", 'wb') as f:
        pickle.dump(data_map, f)
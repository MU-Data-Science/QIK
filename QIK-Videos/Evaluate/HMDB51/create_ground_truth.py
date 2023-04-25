# Imports
import glob
import pickle

# Configurations
METADATA_DIR = "/mydata/HMDB51_Metadata"

if __name__ == "__main__":
    # Initializing the dictionaries to hold the ground truth
    action_dict = {}
    ground_truth = {}

    # Iterating over the files in the directory
    for filepath in glob.iglob(METADATA_DIR + "/*.txt"):
        with open(filepath) as fp:
            # Obtaining the action
            action = filepath.split("/")[-1].split("_test_")[0]

            # Iterating over the metatdata for a particular action.
            lines = fp.readlines()
            for line in lines:
                file_name = line.strip().split(" ")[0]
                # Add to the action dict
                if action in action_dict:
                    file_lst = action_dict[action]
                    file_lst.append(file_name)
                    action_dict[action] = file_lst
                else:
                    action_dict[action] = [file_name]

    # Iterating over the action for creating the ground truth
    for action in action_dict:
        file_lst = action_dict[action]

        # Iterating over all the files belonging to an action
        for file_name in file_lst:
            # All files having the same action is considered as the ground truth
            ground_truth[file_name] = file_lst

    # Saving the ground truth as a pickle file
    with open("hmdb51_groundtruth.pickle", 'wb') as f:
        pickle.dump(ground_truth, f)

    print("create_ground_truth.py :: completed")


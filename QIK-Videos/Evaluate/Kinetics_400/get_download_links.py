# Imports
import json
import subprocess
import os

# Constants
DATA_DIR = "kinetics400"

if __name__ == "__main__":

    # Reading the Training, Validation and Testing files
    train_file = open(DATA_DIR + '/train.json')
    val_file = open(DATA_DIR + '/validate.json')
    test_file = open(DATA_DIR + '/test.json')

    # Loading the JSON files
    train_data = json.load(train_file)
    val_data = json.load(val_file)
    test_data = json.load(test_file)

    # Obtaining the training data.
    for key in train_data:
        download_url = train_data[key]["url"]
        start_time = train_data[key]["annotations"]["segment"][0]
        end_time = train_data[key]["annotations"]["segment"][1]

        # Writing results to the file
        with open('Kinetics_Train.csv', 'a+') as f:
            f.write(key + "," + str(download_url) + "," + str(start_time) + "," + str(end_time) + "\n")

    # Obtaining the validation data.
    for key in val_data:
        download_url = val_data[key]["url"]
        start_time = val_data[key]["annotations"]["segment"][0]
        end_time = val_data[key]["annotations"]["segment"][1]

        # Writing results to the file
        with open('Kinetics_Val.csv', 'a+') as f:
            f.write(key + "," + str(download_url) + "," + str(start_time) + "," + str(end_time) + "\n")

    # Obtaining the test data.
    for key in test_data:
        download_url = test_data[key]["url"]
        start_time = test_data[key]["annotations"]["segment"][0]
        end_time = test_data[key]["annotations"]["segment"][1]

        # Writing results to the file
        with open('Kinetics_Test.csv', 'a+') as f:
            f.write(key + "," + str(download_url) + "," + str(start_time) + "," + str(end_time) + "\n")

    # Closing the files.
    train_file.close()
    val_file.close()
    test_file.close()

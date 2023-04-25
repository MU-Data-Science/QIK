# Imports
from sys import path
path.append("../../QIK_Web/util")
path.append("../../ML_Models/ShowAndTell/im2txt")

import glob
import os
import qik_search

# Constants
DATA_DIR = "/mydata/Kinetics_Eval_Data"
K=5

if __name__ == "__main__":

    # Iterating over all the files.
    for filepath in glob.iglob(DATA_DIR + "/*.mp4"):
        # Obtaining the file name
        file_name = os.path.basename(filepath)
        print("eval.py :: file_name :: ", file_name)

        # QIK Search on the file.
        qik_search.qik_search(filepath, fetch_count = K)

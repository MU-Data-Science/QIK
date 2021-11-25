# Imports
from sys import path
path.append("../Hadamard-Matrix-for-hashing")

import torch
import accimage
import os
import datetime
import numpy as np
import pre_process as prep
from PIL import Image
from torch.autograd import Variable
from pathlib import Path

DATA_DIR = "/mydata/MSCOCO_Dataset/QIK_Image_Data"
# DATA_DIR = "/mydata/MSCOCO_Dataset_Subset"

def pil_loader(path):
    # open path as file to avoid ResourceWarning (https://github.com/python-pillow/Pillow/issues/835)
    with open(path, 'rb') as f:
        with Image.open(f) as img:
            return img.convert('RGB')


def accimage_loader(path):
    try:
        return accimage.Image(path)
    except IOError:
        # Potentially a decoding problem, fall back to PIL.Image
        return pil_loader(path)


# To obtain the hash code
def predict_hash_code(model, input):
    model.eval()
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


# Compute central similarity
def get_similarity(database_hash_lst, query_hash_lst):
    db = convert_list(database_hash_lst)
    q = convert_list(query_hash_lst)
    sim = np.dot(db, q.T)
    ids = np.argsort(-sim, axis=0)
    return ids

if __name__ == '__main__':
    database_hash_lst = []
    file_lst = []

    # Loading the model
    model = torch.load("coco_64bit_0.8612_resnet50.pkl", map_location='cpu')
    model = torch.nn.DataParallel(model).module.to(torch.device("cpu"))
    model = model.module

    # Iterating over the images in the directory
    for filename in os.listdir(DATA_DIR):
        print("Obtaining the features for the image :: " + filename)
        # Loading the image
        img = pil_loader(DATA_DIR + "/" + filename)

        # Transforming the image
        transform = prep.image_test(resize_size=255, crop_size=224)
        input = transform(img)

        # Hack for batch size
        input = input.unsqueeze(0)

        # Obtaining the hash
        try:
            database_hash = predict_hash_code(model, input)
            database_hash_lst.append(database_hash)
            file_lst.append(filename)
        except Exception as e:
            print("eval_HMFH.py :: Skipping file : ", filename)
            print(e)

    # Clearing the results file, if it exists
    if Path("CSQ_Pre_Results_Dict.txt").exists():
        os.remove("CSQ_Pre_Results_Dict.txt")


    # Iterating over the query images
    for filename in os.listdir(DATA_DIR):
        # Noting the start time
        time = datetime.datetime.now()

        # Initializing an array to hold the search results
        result_lst = []

        # Loading the image
        print("Obtaining the features for the query :: " + filename)
        img = pil_loader(DATA_DIR + "/" + filename)

        # Transforming the image
        transform = prep.image_test(resize_size=255, crop_size=224)
        input = transform(img)

        # Hack for batch size
        input = input.unsqueeze(0)

        try:
            # Obtaining the hash
            query_hash = predict_hash_code(model, input)

            # Creating the query hash list
            query_hash_lst = [query_hash]

            # Obtaining the central similariy
            ids = get_similarity(database_hash_lst, query_hash_lst)

            # Iterating over the ids
            for id in ids:
                result_lst.append(file_lst[id[0]])

            # Removing the query from the result list.
            result_lst.remove(filename)

            # Obtaining the CSQ retrieval time
            csq_time = datetime.datetime.now() - time

            # Writing results to the file
            with open('CSQ_Pre_Results_Dict.txt', 'a+') as f:
                f.write(filename + ":: {\'csq_time\': " + str(csq_time.microseconds) +",\'csq_results\': " + str(result_lst[:16]) + "}\n")

        except Exception as e:
            print("eval_HMFH.py :: Skipping file : ", filename)
            print(e)

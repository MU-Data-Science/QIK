import os
import pickle

# Constants.
COCO_TRAIN_PREFIX = "/mydata/im2txt/data/mscoco/raw-data/train2014/COCO_train2014_"
COCO_VAL_PREFIX = "/mydata/im2txt/data/mscoco/raw-data/train2014/COCO_val2014_"
DATA_PKL = "/QIK/Evaluation/data/coco_indexed_subset.pkl"

if __name__ == '__main__':
    # Loading the subset of images.
    image_subset = pickle.load(open(os.environ.get('HOME') + "/" + DATA_PKL, "rb"))

    for img in image_subset:
        if os.path.exists(COCO_TRAIN_PREFIX + img):
            os.remove(COCO_TRAIN_PREFIX + img)
        elif os.path.exists(COCO_VAL_PREFIX + img):
            os.remove(COCO_TRAIN_PREFIX + img)
        else:
            print("The file does not exist. Please recheck.")

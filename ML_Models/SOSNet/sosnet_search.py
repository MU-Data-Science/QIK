import torch
import sosnet_model
import os
import cv2
import tfeat_utils
import pickle
import sosnet_constants

# Global Variables
is_initialized = False
img_dict = {}
sosnet32 = None


# Initializing SOSNet.
def init():
    global is_initialized, img_dict, sosnet32

    if not is_initialized:
        is_initialized = True
        torch.no_grad()

        # Init the 32x32 version of SOSNet.
        sosnet32 = sosnet_model.SOSNet32x32()
        net_name = 'notredame'
        sosnet32.load_state_dict(torch.load(os.path.join('sosnet-weights', "sosnet-32x32-" + net_name + ".pth")),
                                 strict=False)
        sosnet32.cuda().eval();

        # Load the images and detect BRISK keypoints using openCV.
        brisk = cv2.BRISK_create(100)

        # Verifying if precomputed features are present.
        if os.path.exists(sosnet_constants.SOSNET_FEATURES_PATH):
            img_dict = pickle.load(open(sosnet_constants.SOSNET_FEATURES_PATH, "rb"))
        else:
            print("sosnet_search.py :: init :: Constructing features for the images")

            for img in os.listdir(sosnet_constants.SOSNET_IMAGE_DIR):
                try:
                    # Loading the images and detecting BRISK keypoints using openCV.
                    image_vec = cv2.imread(sosnet_constants.SOSNET_IMAGE_DIR + '{}'.format(img), 0)
                    kp = brisk.detect(image_vec, None)

                    # Using the tfeat_utils method to rectify patches around openCV keypoints.
                    desc_tfeat = tfeat_utils.describe_opencv(sosnet32, image_vec, kp, patch_size=32, mag_factor=3)

                    img_dict[img] = desc_tfeat
                except Exception as e:
                    print(e)
                    print("sosnet_search.py :: init :: Error while indexing :: ", img)

            with open(sosnet_constants.SOSNET_FEATURES_PATH, 'wb') as handle:
                pickle.dump(img_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

            print("sosnet_search.py :: init :: Finished processing ", len(img_dict), "images")

def sosnet_search(query_image, k):
    # Initializing the variables
    rank_dict = {}
    ret_list = []

    # Load the images and detect BRISK keypoints using openCV.
    brisk = cv2.BRISK_create(100)
    query_image_vec = cv2.imread(query_image, 0)
    kp = brisk.detect(query_image_vec, None)

    # Rectifying patches around openCV keypoints.
    desc_tfeat = tfeat_utils.describe_opencv(sosnet32, query_image_vec, kp, patch_size=32, mag_factor=3)

    bf = cv2.BFMatcher(cv2.NORM_L2)
    for key in img_dict:
        try:
            matches = bf.knnMatch(desc_tfeat, img_dict[key], k=2)
            # Apply SIFT's ratio test, notice that 0.8 may not be the best ratio for SOSNet
            good = []
            for m, n in matches:
                if m.distance < 0.8 * n.distance:
                    good.append([m])

            # Adding to the candidate list only when there are features matching.
            if len(good) != 0:
                rank_dict[key] = len(good)

        except Exception as e:
            print(e)
            print("sosnet_search.py :: sosnet_search :: Error while matching :: ", key)

    # Sorting the output based on the number of matches
    for fea in sorted(rank_dict, key=rank_dict.get, reverse=True):
        ret_list.append(fea)

    return ret_list[:k]

if __name__ == "__main__":
    print("sosnet_search.py :: main :: start")

    # Initializing.
    init()

    # Starting the index construction.
    results = sosnet_search("/mydata/apache-tomcat/webapps/QIK_Image_Data/000000233566.jpg", 5)
    print("sosnet_search.py :: main :: results :: ", results)
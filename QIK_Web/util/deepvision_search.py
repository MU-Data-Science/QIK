import requests
import constants

def deepvision_search(input_image, fetch_limit):
    # Return list
    ret_lst = []
    # Posting the request to the deepvision server (with GPU)
    with open(input_image, 'rb') as f:
        res = requests.post(constants.DEEPVISION_URL, files={'file': f}, data={'lim': fetch_limit})
        response_lst = str(res.content)[1:].split(" ")

        for image in response_lst:
            ret_lst.append(constants.TOMCAT_IP_ADDR + constants.IMAGE_DATA_DIR + image.split("/")[-1])

    return ret_lst
from sys import path
path.append("../QIK_Web/util/")
path.append("../ML_Models/ObjectDetection")

from qik_search import qik_search
import caption_generator
import detect_objects
import delf_search
import dir_search
import create_qik_results

if __name__ == '__main__':

    # Initializing the ML Models.
    caption_generator.init()
    detect_objects.init()
    delf_search.init()
    # dir_search.init()

    # Verifying QIK.
    image = "000000000077.jpg"
    create_qik_results.retrieve(image)
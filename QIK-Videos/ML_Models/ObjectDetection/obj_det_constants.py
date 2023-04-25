import os

MODEL_NAME = 'faster_rcnn_nas_coco_2018_01_28'
MODEL_FILE = MODEL_NAME + '.tar.gz'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'
FROZEN_GRAPH = 'frozen_inference_graph.pb'
PATH_TO_FROZEN_GRAPH = MODEL_NAME + '/' + FROZEN_GRAPH
PATH_TO_LABELS = os.environ["QIK_HOME"] + '/ML_Models/ObjectDetection/data/mscoco_label_map.pbtxt'
MAX_OBJECTS = 10
MIN_SCORE_THRESHOLD = .90
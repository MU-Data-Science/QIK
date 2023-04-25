# Imports
import numpy as np
import os
import six.moves.urllib as urllib
import tarfile
import tensorflow as tf
from PIL import Image
import obj_det_constants
from util import label_map_util

is_initialized = False
category_index = None
detection_graph = None

# Initializing the model.
def init():
  global is_initialized, category_index, detection_graph

  if not is_initialized:
    # Download the model.
    opener = urllib.request.URLopener()
    opener.retrieve(obj_det_constants.DOWNLOAD_BASE + obj_det_constants.MODEL_FILE, obj_det_constants.MODEL_FILE)
    tar_file = tarfile.open(obj_det_constants.MODEL_FILE)
    for file in tar_file.getmembers():
      file_name = os.path.basename(file.name)
      if obj_det_constants.FROZEN_GRAPH in file_name:
        tar_file.extract(file, os.getcwd())

    # Load the model into memory.
    detection_graph = tf.Graph()
    with detection_graph.as_default():
      od_graph_def = tf.GraphDef()
      with tf.gfile.GFile(obj_det_constants.PATH_TO_FROZEN_GRAPH, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    # Load the  label map
    category_index = label_map_util.create_category_index_from_labelmap(obj_det_constants.PATH_TO_LABELS, use_display_name=True)
    is_initialized = True

# Converting the image into a numpy array.
def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)

def run_inference_for_single_image(image, graph):
  with graph.as_default():
    with tf.Session() as sess:
      # Get handles to input and output tensors
      ops = tf.get_default_graph().get_operations()
      all_tensor_names = {output.name for op in ops for output in op.outputs}
      tensor_dict = {}
      for key in ['detection_scores','detection_classes']:
        tensor_name = key + ':0'
        if tensor_name in all_tensor_names:
          tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
              tensor_name)
      image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

      # Run inference
      output_dict = sess.run(tensor_dict,
                             feed_dict={image_tensor: image})

      # all outputs are float32 numpy arrays, so convert types as appropriate
      output_dict['detection_classes'] = output_dict[
          'detection_classes'][0].astype(np.int64)
  return output_dict

def get_detected_objects(input_image, threshold = obj_det_constants.MIN_SCORE_THRESHOLD):
  # List of objects detected
  ret_lst = []

  # Converting the image to a numpy array.
  image_np = load_image_into_numpy_array(Image.open(input_image))

  # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
  image_np_expanded = np.expand_dims(image_np, axis=0)

  # Actual detection.
  output_dict = run_inference_for_single_image(image_np_expanded, detection_graph)

  # Score of the object
  scores = output_dict['detection_scores'][0]

  # Adding the objects detected to a list.
  for i in range(obj_det_constants.MAX_OBJECTS):
    if scores[i] > threshold:
      detected_class = category_index[output_dict['detection_classes'][i]]['name']
      if detected_class not in ret_lst:
        ret_lst.append(category_index[output_dict['detection_classes'][i]]['name'])

  return ret_lst

if __name__ == '__main__':
  # Initializing the model.
  init()

  # Input image.
  image = "/mydata/apache-tomcat/webapps/QIK_Image_Data/000000211546.jpg"

  print(get_detected_objects(image))

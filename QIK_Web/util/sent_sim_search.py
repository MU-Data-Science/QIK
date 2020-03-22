import caption_generator
import tensorflow as tf
import tensorflow_hub as hub
import constants
import faiss
import pickle
import numpy as np

is_initialized = False
index = None
embed = None
session = None
file_lst = []

def init():
  print("sent_sim_search :: init :: Start")

  global is_initialized, embed, session, index, file_lst

  # Setting logging level.
  tf.logging.set_verbosity(tf.logging.ERROR)

  if not is_initialized:
      # Loading the Show and Tell Model.
      caption_generator.init()

      # Import the Universal Sentence Encoder's TF Hub module
      embed = hub.Module(constants.SENT_SIM_MODULE_URL)

      session = tf.Session()
      session.run([tf.global_variables_initializer(), tf.tables_initializer()])
      is_initialized = True

      # Loading the FAISS Index.
      index = faiss.read_index(constants.FAISS_INDEX_PATH)

      # Loading the file list.
      file_lst = pickle.load(open(constants.FAISS_FILE_LST_PATH, "rb"))

  print("sent_sim_search :: init :: End")

def query(query_image, fetch_count=constants.FAISS_FETCH_LIMIT):
    print("sent_sim_search :: query :: Start")

    # Generating the caption for the query image.
    caption = caption_generator.get_caption(query_image, True)

    # Constructing the embedding for the caption.
    embedding = session.run(embed([caption]))

    xq = np.vstack(np.array(embedding).tolist()).astype('float32')
    xq[:, 0] += np.arange(1) / 1000.

    # Actual KNN search.
    D, I = index.search(xq, fetch_count)

    # Iterating over the results.
    ret_lst = []
    for ind in I[0]:
        # Printing the results
        ret_lst.append(file_lst[ind])

    print("sent_sim_search :: query :: ret_lst :: ", ret_lst)
    return ret_lst
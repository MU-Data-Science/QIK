from sys import path
path.append("../../QIK_Web/util")

import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import os
import sent_sim_constants
import caption_generator
import faiss
import pickle
import requests
import json

is_initialized = False
embed = None
session = None

def init():
  print("sentence_similarity_index :: init :: Start")

  global is_initialized, embed, session

  # Setting logging level.
  tf.logging.set_verbosity(tf.logging.ERROR)

  if not is_initialized:
      # Loading the Show and Tell Model.
      caption_generator.init()

      # Import the Universal Sentence Encoder's TF Hub module
      embed = hub.Module(sent_sim_constants.SENT_SIM_MODULE_URL)

      session = tf.Session()
      session.run([tf.global_variables_initializer(), tf.tables_initializer()])
      is_initialized = True

  print("sentence_similarity_index :: init :: End")


def index(index_dir = sent_sim_constants.IMAGE_DIR):
    sentences_lst = []
    embeddings_lst = []
    file_lst = []

    # Iterating over the images in the directory.
    for file in os.listdir(os.fsencode(index_dir)):
        # Getting the complete image path
        filename = index_dir + os.fsdecode(file)
        print("sentence_similarity_index :: Executing :: ", filename)

        # Adding the file to the list.
        file_lst.append(filename)

        # Generating the captions for the images using the caption generator.
        # caption_str = caption_generator.get_caption(filename, True)
        # print("sentence_similarity_index :: caption_str :: ", caption_str)
        # Adding the sentences to the list.
        # sentences_lst.append(caption_str)

        # Fetching the captions for the images from SOLR.
        res = json.loads(requests.get("http://128.105.144.53:8983/solr/QIK/select?q=key%3A" + os.fsdecode(file).split(".")[0]).text)
        print("res :: ", res)
        if res['response']['numFound'] > 0:
            print("Generated Caption :: ", res['response']['docs'][0]['caption'][0])
            sentences_lst.append(res['response']['docs'][0]['caption'][0])

    # Constructing the embeddings for the sentences.
    print("sentence_similarity_index :: Constructing the Embedding")
    message_embeddings = session.run(embed(sentences_lst))

    for message_embedding in np.array(message_embeddings).tolist():
        embeddings_lst.append(message_embedding)

    print("sentence_similarity_index :: Constructing the Index")
    xb = np.vstack(embeddings_lst).astype('float32')
    xb[:, 0] += np.arange(len(sentences_lst)) / 1000.

    # Building the index.
    index = faiss.IndexFlatL2(sent_sim_constants.D)
    index.add(xb)

    # Saving the index.
    faiss.write_index(index, "sent_sim.index")
    print("sentence_similarity_index :: Completed index Construction.")

    # Saving the files list.
    with open('files.pkl', 'wb') as f:
        pickle.dump(file_lst, f)

if __name__ == "__main__":
    print("sentence_similarity_index :: main :: start")

    # Initializing.
    init()

    # Starting the index construction.
    index("/mydata/apache-tomcat/webapps/QIK_Image_Data/")
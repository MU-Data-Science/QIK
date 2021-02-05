from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import os
from sys import path
path.append("../ML_Models/ShowAndTell/im2txt")

import tensorflow as tf

from im2txt import configuration
from im2txt import inference_wrapper
from im2txt.inference_utils import caption_generator
from im2txt.inference_utils import vocabulary

FLAGS = None
sess = None
vocab = None
g = None
generator = None
is_initialized = False

def init():
  print("caption_generator :: init :: Start")

  global sess, vocab, model, g, generator, is_initialized

  if not is_initialized:
    is_initialized = True

    FLAGS = tf.flags.FLAGS

    if 'checkpoint_path' not in tf.flags.FLAGS.__flags:
      tf.flags.DEFINE_string("checkpoint_path", "../ML_Models/ShowAndTell/checkpoints/",
                           "Model checkpoint file or directory containing a "
                           "model checkpoint file.")
    if 'vocab_file' not in tf.flags.FLAGS.__flags:
      tf.flags.DEFINE_string("vocab_file", "../ML_Models/ShowAndTell/checkpoints/word_counts.txt",
                           "Text file containing the vocabulary.")

    tf.logging.set_verbosity(tf.logging.INFO)

    # Build the inference graph.
    g = tf.Graph()
    with g.as_default():
      model = inference_wrapper.InferenceWrapper()
      restore_fn = model.build_graph_from_config(configuration.ModelConfig(),
                                                 FLAGS.checkpoint_path)
    g.finalize()

    # Create the vocabulary.
    vocab = vocabulary.Vocabulary(FLAGS.vocab_file)

    # Load the model from checkpoint.
    sess = tf.Session(graph=g)
    restore_fn(sess)

    # Prepare the caption generator. Here we are implicitly using the default
    # beam search parameters. See caption_generator.py for a description of the
    # available beam search parameters.
    generator = caption_generator.CaptionGenerator(model, vocab)

    print("caption_generator :: init :: End")

def get_caption(filename, get_top_caption):
  print("Entering captions for :: ", filename)

  global sess, vocab, generator

  with tf.gfile.GFile(filename, "rb") as f:
    image = f.read()
    captions = generator.beam_search(sess, image)

    sentences = []
    retStr = "Captions for image %s:" % os.path.basename(filename) + "\n"
    for i, caption in enumerate(captions):
      # Ignore begin and end words.
      sentence = [vocab.id_to_word(w) for w in caption.sentence[1:-1]]
      sentence = " ".join(sentence)
      sentences.append(sentence)
      retStr += "  %d) %s (p=%f)" % (i, sentence, math.exp(caption.logprob)) + "\n"

    # Returning the topmost caption.
    if get_top_caption == True:
      return sentences[0]
    else:
      return retStr


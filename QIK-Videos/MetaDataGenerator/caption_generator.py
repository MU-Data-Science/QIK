from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import os
from sys import path
path.append("../ML_Models/ShowAndTell/im2txt")

import tensorflow as tf
import constants

from im2txt import configuration
from im2txt import inference_wrapper
from im2txt.inference_utils import caption_generator
from im2txt.inference_utils import vocabulary

FLAGS = tf.flags.FLAGS

tf.flags.DEFINE_string("checkpoint_path", constants.CHECKPOINT_PATH,
                       "Model checkpoint file or directory containing a "
                       "model checkpoint file.")
tf.flags.DEFINE_string("vocab_file", constants.VOCAB_FILE, "Text file containing the vocabulary.")

tf.logging.set_verbosity(tf.logging.INFO)

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

def get_caption(filename):
  print("caption_generator :: get_caption :: Start")
  
  with tf.gfile.GFile(filename, "rb") as f:
      image = f.read()
      captions = generator.beam_search(sess, image)

      captions_str = ""

      print("caption_generator :: get_caption :: Captions for image %s :: " % os.path.basename(filename))
      captions_str = captions_str + "Captions for image %s:" % os.path.basename(filename) + "\n"
      for i, caption in enumerate(captions):
        # Ignore begin and end words.
        sentence = [vocab.id_to_word(w) for w in caption.sentence[1:-1]]
        sentence = " ".join(sentence)
        print("  %d) %s (p=%f)" % (i, sentence, math.exp(caption.logprob)))
        captions_str = captions_str + "  %d) %s (p=%f)" % (i, sentence, math.exp(caption.logprob)) + "\n"

      # Returning the caption string.
      return captions_str

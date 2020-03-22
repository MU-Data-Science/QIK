import tensorflow as tf
import tensorflow_ranking as tfr
import os

tf.enable_eager_execution()
tf.executing_eagerly()
tf.logging.set_verbosity(tf.logging.DEBUG)

# Store the paths to files containing training and test instances.
# As noted above, we will assume the data is in the LibSVM format
# and that the content of each file is sorted by query ID.
_TRAIN_DATA_PATH="data/train.txt"
_TEST_DATA_PATH="data/test.txt"
MODEL_DIR="checkpoints"

# Define a loss function. To find a complete list of available
# loss functions or to learn how to add your own custom function
# please refer to the tensorflow_ranking.losses module.
_LOSS="pairwise_logistic_loss"

# In the TF-Ranking framework, a training instance is represented
# by a Tensor that contains features from a list of documents
# associated with a single query. For simplicity, we fix the shape
# of these Tensors to a maximum list size and call it "list_size,"
# the maximum number of documents per query in the dataset.
# In this demo, we take the following approach:
#   * If a query has fewer documents, its Tensor will be padded
#     appropriately.
#   * If a query has more documents, we shuffle its list of
#     documents and trim the list down to the prescribed list_size.
_LIST_SIZE=100

# The total number of features per query-document pair.
# We set this number to the number of features in the MSLR-Web30K
# dataset.
_NUM_FEATURES=136

# Parameters to the scoring function.
_BATCH_SIZE=32
_HIDDEN_LAYER_DIMS=["20", "10"]

def input_fn(path):
  train_dataset = tf.data.Dataset.from_generator(
      tfr.data.libsvm_generator(path, _NUM_FEATURES, _LIST_SIZE),
      output_types=(
          {str(k): tf.float32 for k in range(1,_NUM_FEATURES+1)},
          tf.float32
      ),
      output_shapes=(
          {str(k): tf.TensorShape([_LIST_SIZE, 1])
            for k in range(1,_NUM_FEATURES+1)},
          tf.TensorShape([_LIST_SIZE])
      )
  )
  train_dataset = train_dataset.shuffle(1000).repeat().batch(_BATCH_SIZE)
  return train_dataset.make_one_shot_iterator().get_next()
  
def example_feature_columns():
  """Returns the example feature columns."""
  feature_names = [
      "%d" % (i + 1) for i in range(0, _NUM_FEATURES)
  ]
  return {
      name: tf.feature_column.numeric_column(
          name, shape=(1,), default_value=0.0) for name in feature_names
  }

def make_score_fn():
  """Returns a scoring function to build `EstimatorSpec`."""

  def _score_fn(context_features, group_features, mode, params, config):
    """Defines the network to score a documents."""
    del params
    del config
    # Define input layer.
    example_input = [
        tf.layers.flatten(group_features[name])
        for name in sorted(example_feature_columns())
    ]
    input_layer = tf.concat(example_input, 1)

    cur_layer = input_layer
    for i, layer_width in enumerate(int(d) for d in _HIDDEN_LAYER_DIMS):
      cur_layer = tf.layers.dense(
          cur_layer,
          units=layer_width,
          activation="tanh")

    logits = tf.layers.dense(cur_layer, units=1)
    return logits

  return _score_fn
  
def eval_metric_fns():
  """Returns a dict from name to metric functions.

  This can be customized as follows. Care must be taken when handling padded
  lists.

  def _auc(labels, predictions, features):
    is_label_valid = tf_reshape(tf.greater_equal(labels, 0.), [-1, 1])
    clean_labels = tf.boolean_mask(tf.reshape(labels, [-1, 1], is_label_valid)
    clean_pred = tf.boolean_maks(tf.reshape(predictions, [-1, 1], is_label_valid)
    return tf.metrics.auc(clean_labels, tf.sigmoid(clean_pred), ...)
  metric_fns["auc"] = _auc

  Returns:
    A dict mapping from metric name to a metric function with above signature.
  """
  metric_fns = {}
  metric_fns.update({
      "metric/ndcg@%d" % topn: tfr.metrics.make_ranking_metric_fn(
          tfr.metrics.RankingMetricKey.NDCG, topn=topn)
      for topn in [1, 3, 5, 10]
  })

  return metric_fns
  
def get_estimator(hparams):
  """Create a ranking estimator.

  Args:
    hparams: (tf.contrib.training.HParams) a hyperparameters object.

  Returns:
    tf.learn `Estimator`.
  """
  def _train_op_fn(loss):
    """Defines train op used in ranking head."""
    return tf.contrib.layers.optimize_loss(
        loss=loss,
        global_step=tf.train.get_global_step(),
        learning_rate=hparams.learning_rate,
        optimizer="Adagrad")

  ranking_head = tfr.head.create_ranking_head(
      loss_fn=tfr.losses.make_loss_fn(_LOSS),
      eval_metric_fns=eval_metric_fns(),
      train_op_fn=_train_op_fn)

  return tf.estimator.Estimator(
      model_fn=tfr.model.make_groupwise_ranking_fn(
          group_score_fn=make_score_fn(),
          group_size=1,
          transform_fn=None,
          ranking_head=ranking_head),
      params=hparams,
      model_dir=MODEL_DIR)

def libsvmgenerator(data, num_features, list_size):
  """Parses a LibSVM-formatted input file and aggregates data points by qid.

  Args:
    path: (string) path to dataset in the LibSVM format.
    num_features: An integer representing the number of features per instance.
    list_size: Size of the document list per query.
    seed: Randomization seed used when shuffling the document list.

  Returns:
    A generator function that can be passed to tf.data.Dataset.from_generator().
  """

  def inner_generator():
    """Produces a generator ready for tf.data.Dataset.from_generator.

    It is assumed that data points in a LibSVM-formatted input file are
    sorted by query ID before being presented to this function. This
    assumption simplifies the parsing and aggregation logic: We consume
    lines sequentially and accumulate query-document features until a
    new query ID is observed, at which point the accumulated data points
    are massaged into a tf.data.Dataset compatible representation.

    Yields:
      A tuple of feature and label `Tensor`s.
    """
    # A buffer where observed query-document features will be stored.
    # It is a list of dictionaries, one per query-document pair, where
    # each dictionary is a mapping from a feature ID to a feature value.
    doc_list = []

    # cur indicates the current query ID.
    cur = -1

    for line in data:
        qid, doc = tfr.data._libsvm_parse_line(line)
        if cur < 0:
          cur = qid

        # If qid is not new store the data and move onto the next line.
        if qid == cur:
          doc_list.append(doc)
          continue

        yield tfr.data._libsvm_generate(
            num_features, list_size, doc_list)

        # Reset current pointer and re-initialize document list.
        cur = qid
        doc_list = [doc]

    yield tfr.data._libsvm_generate(num_features, list_size, doc_list)

  return inner_generator

def getTFData(data):
  tfdata = tf.data.Dataset.from_generator(
      libsvmgenerator(data, _NUM_FEATURES, len(data)),
      output_types=(
          {str(k): tf.float32 for k in range(1,_NUM_FEATURES+1)},
          tf.float32
      ),
      output_shapes=(
          {str(k): tf.TensorShape([len(data), 1])
            for k in range(1,_NUM_FEATURES+1)},
          tf.TensorShape([len(data)])
      )
  )
  return tfdata

def getRanking(inp):
    hparams = tf.contrib.training.HParams(learning_rate=0.05)
    ranker = get_estimator(hparams)

    if len(os.listdir(MODEL_DIR)) == 0:
        print("Trained model not found. Retraining.")
        ranker.train(input_fn=lambda: input_fn(_TRAIN_DATA_PATH), steps=100)
        ranker.evaluate(input_fn=lambda: input_fn(_TEST_DATA_PATH), steps=100)

    for x in ranker.predict(input_fn=lambda: getTFData(inp)):
        print(x)

    
if __name__ == "__main__":
    inp = [
        "1 qid:1 131:0.680359 37:0.378269 40:-0.105563 90:-0.223249 7:0.228429 107:0.108382 82:-0.801387 54:0.254594 2:-0.713251 2:0.498115 43:0.405978 46:0.350666 61:0.220473 37:0.787291 81:-0.455612 46:-0.605197 82:-0.876627 77:-0.508701 93:-0.285024",
        "2 qid:1 54:0.495344 21:0.573252 109:0.230595 15:0.640667 85:0.468381 29:0.965446 82:-0.895478 62:0.566129 29:-0.168279 80:-0.104614 1:0.458963 57:-0.137389 126:-0.185907 67:0.467317 39:-0.385899 12:0.789948 132:0.168467 103:0.103821 8:0.919103",
        "0 qid:1 111:0.705173 25:-0.509040 108:0.635695 4:0.650918 4:0.219718 111:-0.058046 16:0.884523 76:0.981032 90:0.196113 63:-0.346408 15:-0.539968 59:-0.792260 11:-0.825289 104:0.194265 31:0.144826 53:-0.535111 92:-0.040113 74:0.375495 16:0.264418",
        "0 qid:1 100:0.721208 110:0.686827 109:0.428681 36:-0.320784 114:0.060694 14:-0.699080 63:0.185759 51:0.276596 19:0.576368 108:-0.397936 104:0.169159 93:0.388789 112:-0.667618 20:-0.791008 94:-0.712865 110:0.846173 126:-0.194097 33:-0.946587 112:-0.637152",
        "1 qid:1 12:-0.591040 9:-0.163267 51:0.417009 121:-0.238818 42:0.612037 26:-0.934430 77:-0.546164 97:0.739583 104:0.760357 131:0.306862 74:0.147403 73:-0.693903 91:-0.897769 123:-0.942796 113:0.407300 31:-0.109243 131:-0.743804 71:0.628323 19:-0.472442"]
    getRanking(inp)
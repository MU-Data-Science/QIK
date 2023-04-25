import tensorflow as tf
import tensorflow_hub as hub
import numpy as np

def getSimilarityScore(inp, sentences):
    tfdict = {}
    sentenceList = [inp]
    thresholdScore = .5 #Setting score as .5 to add only those results that match better

    for sent in sentences:
        sentenceList.append(sent)

    module_url = "https://tfhub.dev/google/universal-sentence-encoder-large/3"

    embed = hub.Module(module_url)
    tf.logging.set_verbosity(tf.logging.ERROR)

    similarity_input_placeholder = tf.placeholder(tf.string, shape=(None))
    similarity_message_encodings = embed(similarity_input_placeholder)

    with tf.Session() as session:
        session.run([tf.global_variables_initializer(), tf.tables_initializer()])
        message_embeddings = session.run(similarity_message_encodings, feed_dict={similarity_input_placeholder: sentenceList})
        corr = np.inner(message_embeddings, message_embeddings)
        print(corr[0])

    for i in range(len(sentences)):
        score = corr[0][i+1]
        if score > thresholdScore:
            tfdict[sentences[i]] = score

    print("tfdict :: ", tfdict)

    return tfdict

def getSentenceSimilarityScore(inp, sentence):
    tfdict = {}
    sentenceList = [inp, sentence]
    thresholdScore = .5 #Setting score as .5 to add only those results that match better

    module_url = "https://tfhub.dev/google/universal-sentence-encoder-large/3"

    embed = hub.Module(module_url)
    tf.logging.set_verbosity(tf.logging.ERROR)

    similarity_input_placeholder = tf.placeholder(tf.string, shape=(None))
    similarity_message_encodings = embed(similarity_input_placeholder)

    with tf.Session() as session:
        session.run([tf.global_variables_initializer(), tf.tables_initializer()])
        message_embeddings = session.run(similarity_message_encodings, feed_dict={similarity_input_placeholder: sentenceList})
        corr = np.inner(message_embeddings, message_embeddings)
        score = corr[0][1]
        print("sentence_similarity :: getSentenceSimilarityScore :: score :: ", score)
        if score > thresholdScore:
            return score
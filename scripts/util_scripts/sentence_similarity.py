import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import sys

sentenceList = []
module_url = "https://tfhub.dev/google/universal-sentence-encoder/2"

embed = hub.Module(module_url)

tf.logging.set_verbosity(tf.logging.ERROR)

similarity_input_placeholder = tf.placeholder(tf.string, shape=(None))
similarity_message_encodings = embed(similarity_input_placeholder)
	
if __name__ == "__main__":
	sentences = sys.argv[1:]
	for sentence in sentences:
		sentenceList.append(sentence)
		
	with tf.Session() as session:
		session.run([tf.global_variables_initializer(), tf.tables_initializer()])
		message_embeddings = session.run(similarity_message_encodings, feed_dict={similarity_input_placeholder: sentenceList})
		corr = np.inner(message_embeddings, message_embeddings)
		print("corr :: ")
		print(corr)
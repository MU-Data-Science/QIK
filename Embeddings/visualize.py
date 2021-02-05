import gensim
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import itertools

EMBEDDING = "data/model.txt"
NEIGHBOURS = 200
# Keys for visualization.
keys = ['zebra', 'cat', 'dog']

def tsne_plot_similar_words(title, labels, embedding_clusters, word_clusters, a, filename=None):
    plt.figure(figsize=(16, 9))
    colors = itertools.cycle(["r", "b", "g"])
    for label, embeddings, words, color in zip(labels, embedding_clusters, word_clusters, colors):
        x = embeddings[:, 0]
        y = embeddings[:, 1]
        plt.scatter(x, y, c=color, alpha=a, label=label)
        for i, word in enumerate(words):
            plt.annotate(word, alpha=0.5, xy=(x[i], y[i]), xytext=(5, 2),
                         textcoords='offset points', ha='right', va='bottom', size=12)
    plt.legend(loc=4)
    plt.title(title)
    plt.grid(False)
    plt.savefig('data/Embedding.png', format='png', dpi=150, bbox_inches='tight')
    plt.show()

if __name__ == '__main__':
    # Loading the converted file.
    model = gensim.models.KeyedVectors.load_word2vec_format(EMBEDDING, binary=False)

    # Retreiving the k nearest words and their embedding for their keys.
    embedding_clusters = []
    word_clusters = []
    for word in keys:
        embeddings = []
        words = []
        for similar_word, _ in model.most_similar(word, topn=NEIGHBOURS):
            words.append(similar_word)
            embeddings.append(model[similar_word])
        embedding_clusters.append(embeddings)
        word_clusters.append(words)

    # Actual TSNE logic.
    embedding_clusters = np.array(embedding_clusters)
    n, m, k = embedding_clusters.shape
    tsne_model_en_2d = TSNE(perplexity=15, n_components=2, init='pca', n_iter=3500, random_state=32)
    embeddings_en_2d = np.array(tsne_model_en_2d.fit_transform(embedding_clusters.reshape(n * m, k))).reshape(n, m, 2)

    tsne_plot_similar_words('Word Embeddings', keys, embeddings_en_2d, word_clusters, 0.7,)
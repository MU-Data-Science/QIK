# Ref: https://medium.com/@ermolushka/text-clusterization-using-python-and-doc2vec-8c499668fa61

# Requirements:
# gensim==3.8.3
# scikit-learn==0.24.2

# Imports
import json
import nltk
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import pickle

# Constants
ANN_FILES = ["/mydata/MSRVTT_Annotations/test_videodatainfo.json", "/mydata/MSRVTT_Annotations/train_val_videodatainfo.json"]
CLUSTERS = [10, 20, 30, 40, 50]

if __name__ == "__main__":
    nltk.download('punkt')

    # Initializing the ground truth dictionary and a list of captions.
    data_dict = {}
    cat_dict = {}
    label_dict = {}
    ground_truth_dict = {}

    # Reading the annotations
    for ann in ANN_FILES:
        with open(ann) as file:
            data = json.load(file)

            # Obtaining all the captions
            sentences = data["sentences"]
            videos = data["videos"]

            # Iterating over the captions
            for sentence in sentences:
                video_id = sentence["video_id"]
                caption = sentence["caption"]

                # If video in the dictionary, append the caption to the list of captions.
                if video_id in data_dict:
                    sent = data_dict[video_id]
                    data_dict[video_id] = sent + " " + caption + "."
                else:
                    # If the video is not in dictionary, add to it.
                    data_dict[video_id] = caption + "."

    for video_id in data_dict:
        for video in videos:
            if video["video_id"] == video_id:
                cat_dict[data_dict[video_id]] = video["category"]

    tagged_data = [TaggedDocument(words=word_tokenize(_d.lower()), tags=[str(i)]) for i, _d in enumerate(data_dict.values())]

    # With detailed hyper parameters provided.
    # d2v_model = Doc2Vec(tagged_data, size=1000, window=10, min_count=500, workers=7, dm=1, alpha=0.025, min_alpha=0.001)
    # d2v_model.train(tagged_data, total_examples=d2v_model.corpus_count, epochs=1000, start_alpha=0.002, end_alpha=-0.016)

    d2v_model = Doc2Vec(tagged_data, size=300, workers=25)
    d2v_model.train(tagged_data, total_examples=d2v_model.corpus_count, epochs=1000)

    for c in CLUSTERS:
        kmeans_model = KMeans(n_clusters=c, init='k-means++', max_iter=100)
        X = kmeans_model.fit(d2v_model.docvecs.doctag_syn0)
        labels = kmeans_model.labels_.tolist()

        # Computing the silhouette score
        silhouette_avg = silhouette_score(d2v_model.docvecs.doctag_syn0, labels)
        print("Silhouette score (n=", c, "): ", silhouette_avg)

        # Plotting the clusters
        pca = PCA(n_components=2).fit(d2v_model.docvecs.doctag_syn0)
        datapoint = pca.transform(d2v_model.docvecs.doctag_syn0)
        plt.scatter(datapoint[:, 0], datapoint[:, 1], c=labels)
        centroids = kmeans_model.cluster_centers_
        centroid_point = pca.transform(centroids)
        plt.scatter(centroid_point[:, 0], centroid_point[:, 1], marker='^', s=20, c='#000000')
        plt.savefig("clusters_" + str(c) + ".png")

        # Obtaining the cluster for each video
        for index, (key, value) in enumerate(data_dict.items()):
            label_dict[key] = labels[index]

        # Creating the ground truth
        for q_video_id in label_dict:
            results = []

            for c_video_id in label_dict:
                if label_dict[c_video_id] == label_dict[q_video_id]:
                    results.append(c_video_id)

            ground_truth_dict[q_video_id] = results

        # Creating the pickle file of the ground truth.
        with open("Clustered_Ground_Truth" + str(c) + ".pkl", "wb") as f:
            pickle.dump(ground_truth_dict, f)

from gensim.models import Word2Vec

model = None

def init():
    global model

    # Initializing caption_lst
    caption_lst = []

    # Reading the captions
    with open("data/120k_Captions.txt") as file:
        for caption in file:
            caption_lst.append(caption.strip().split(" "))

    # Training the model
    model = Word2Vec(caption_lst, min_count=1)

    # Saving the model
    model.wv.save_word2vec_format('data/model.txt')

def getNearestNeighbours(word, k=5):
    # Initializing a return list.
    ret_lst = []

    # Get nearest neighbours.
    results = model.similar_by_word(word, topn=k)
    for result in results:
        ret_lst.append(result[0])

    return ret_lst

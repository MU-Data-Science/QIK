# Imports.
import os
import faiss
import numpy as np
from keras.preprocessing import image
import encoder
import pickle

# Dimensions. (256 X 256 X 3)
d = 196608

# No of queries.
nq = 1

# No of nearest neighbors to be fetched.
k=5

# Images directory path
cand_img_path="/dev/data/apache-tomcat/webapps/flickr30k_images/flickr30k_images/"
input_img="/dev/data/apache-tomcat/webapps/flickr30k_images/flickr30k_images/3333921867.jpg"

# Image Arrays
vector_arr = [] 
image_arr = []

# Iterating over the images in the directory.
folder = os.fsencode(cand_img_path)
for file in os.listdir(folder):
    filename = cand_img_path + os.fsdecode(file)
        
    # Using the auto-encoder model to convert the images to a vector.
    vector = encoder.get_img(filename)
    pred_vector = encoder.model.predict(vector)
	
    # Reshaping the image vector.
    reshaped_arr = pred_vector[0].reshape(d)
    
    # Adding the reshaped array to a list.
    vector_arr.append(reshaped_arr)
    
    # Adding the image to the image dictionary.
    image_arr.append(filename)
    print("Completed one")

with open("/dev/data/files.txt", "wb") as fp:
    pickle.dump(image_arr, fp)

print("Completed forming the database")    
# Database size. (Should be according to the number of images in the database)
#nb = len(vector_arr)   
        
# Database matrix that contains all the vectors that needs to be indexed.
#xb = np.vstack(vector_arr)
#xb[:, 0] += np.arange(nb) / 1000.

#Building the index.
#index = faiss.IndexFlatL2(d)

# Saving the index
#faiss.write_index(index, "index/knn.index")

# Reading the index
index = faiss.read_index("/dev/data/KNN_Index/knn.index")
print(index.is_trained)

# Adding vectors to the index.
#index.add(xb)
print(index.ntotal)

#faiss.write_index(index, "/dev/data/KNN_Index/knn.index")

# Converting the input image to a vector.
vector = encoder.get_img(input_img)
pred_vector = encoder.model.predict(vector)

# Reshaping the image vector.
reshaped_arr = pred_vector[0].reshape(d)

# Matrix containing the query vectors.
xq = np.vstack([reshaped_arr])
xq[:, 0] += np.arange(nq) / 1000.

# Actual KNN search.
D, I = index.search(xq, k)

# Iterating over the results.
for index in I[0]:
	# Printing the results
	print(image_arr[index])

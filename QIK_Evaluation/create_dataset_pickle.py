# imports
import pickle
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Preprocess to extract text from a folder of csv files.')
    parser.add_argument('-data', default="data/15K_Dataset.txt", metavar='data', help='File containing list of images.', required=False)
    parser.add_argument('-out', default="data/15K_Dataset.pkl", metavar='data', help='Pickled file.', required=False)
    args = parser.parse_args()


    image_lst = []
    # Opening the list of images that have been indexed.
    file = open(args.data, "r")

    # Iterating over the images.
    for image in file:
        image_lst.append(image.rstrip())

    # Closing the file.
    file.close()

    # Adding the data to a pickle file.
    with open(args.out, "wb") as f:
        pickle.dump(image_lst, f)

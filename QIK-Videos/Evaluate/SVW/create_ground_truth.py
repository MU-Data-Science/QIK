# pandas==1.1.5

import pandas as pd
import pickle

ANN_FILE = "SVW.csv"

if __name__ == "__main__":
    df = pd.read_csv(ANN_FILE)

    category_dict = {}

    for index, row in df.iterrows():
        if not pd.isnull(row['FileName']):
            file_name = row['FileName'][:-4]
            if row['Genre'] in category_dict:
                lst = category_dict[row['Genre']]
                lst.append(file_name)
                category_dict[row['Genre']] = lst
            else:
                category_dict[row['Genre']] = [file_name]

    print(category_dict)
    # Creating the pickle file of the ground truth.
    with open("SVW_Ground_Truth.pkl", "wb") as f:
        pickle.dump(category_dict, f)


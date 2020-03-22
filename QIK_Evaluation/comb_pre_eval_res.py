# Imports
import json
import pickle

# Constants.
QIK_PRE_RESULTS_FILE = "data/MSCOCO_Subset_2/QIK_Captions_Pre_Results_Dict.txt"
QIK_OBJECTS_PRE_RESULTS_FILE = "data/MSCOCO_Subset_2/QIK_Objects_9_Pre_Results_Dict.txt"
DV_PRE_RESULTS_FILE = "data/MSCOCO_Subset_2/Deep_Vision_Pre_Results_Dict.txt"
DELF_PRE_RESULTS_FILE = "data/MSCOCO_Subset_2/DELF_Pre_Results_Dict.txt"
LIRE_PRE_RESULTS_FILE = "data/MSCOCO_Subset_2/LIRE_Pre_Results_Dict.txt"
DIR_PRE_RESULTS_FILE = "data/MSCOCO_Subset_2/DIR_Pre_Results_Dict.txt"
CROW_PRE_RESULTS_FILE = "data/MSCOCO_Subset_2/Crow_Pre_Results_Dict.txt"
OUT_FILE = "data/MSCOCO_Subset_2/MSCOCO_Subset_2_Results.pkl"

if __name__ == '__main__':
    # Combined Results Dictionary.
    results_dict = {}

    # Iterating over QIK Results.
    qik_results_dict = {}
    results = open(QIK_PRE_RESULTS_FILE, "r")
    for result in results:
        qik_results_dict[result.split("::")[0].strip()] = json.loads(result.split("::")[1].replace("'",'"'))
    print("qik_results_dict :: ", qik_results_dict)

    # Iterating over QIK Objects Results.
    qik_objects_results_dict = {}
    results = open(QIK_OBJECTS_PRE_RESULTS_FILE, "r")
    for result in results:
        qik_objects_results_dict[result.split("::")[0].strip()] = json.loads(result.split("::")[1].replace("'", '"'))
    print("qik_objects_results_dict :: ", qik_objects_results_dict)

    # Iterating over DeepVision Results.
    dv_results_dict = {}
    results = open(DV_PRE_RESULTS_FILE, "r")
    for result in results:
        dv_results_dict[result.split("::")[0].strip()] = json.loads(result.split("::")[1].replace("'", '"'))
    print("dv_results_dict :: ", dv_results_dict)

    # Iterating over DELF Results.
    delf_results_dict = {}
    results = open(DELF_PRE_RESULTS_FILE, "r")
    for result in results:
        delf_results_dict[result.split("::")[0].strip()] = json.loads(result.split("::")[1].replace("'", '"'))
    print("delf_results_dict :: ", delf_results_dict)

    # Iterating over LIRE Results.
    lire_results_dict = {}
    results = open(LIRE_PRE_RESULTS_FILE, "r")
    for result in results:
        lire_results_dict[result.split("::")[0].strip()] = json.loads(result.split("::")[1].replace("'", '"'))
    print("lire_results_dict :: ", lire_results_dict)

    # Iterating over DIR Results.
    dir_results_dict = {}
    results = open(DIR_PRE_RESULTS_FILE, "r")
    for result in results:
        dir_results_dict[result.split("::")[0].strip()] = json.loads(result.split("::")[1].replace("'", '"'))
    print("dir_results_dict :: ", dir_results_dict)

    # Iterating over CROW Results.
    crow_results_dict = {}
    results = open(CROW_PRE_RESULTS_FILE, "r")
    for result in results:
        crow_results_dict[result.split("::")[0].strip()] = json.loads(result.split("::")[1].replace("'", '"'))
    print("crow_results_dict :: ", crow_results_dict)

    # Combining all the results.
    for image in qik_results_dict:
        if image in qik_objects_results_dict and image in dv_results_dict and image in delf_results_dict and image in lire_results_dict and image in dir_results_dict and image in crow_results_dict:
            results_dict[image] = {**qik_results_dict[image], **qik_objects_results_dict[image], **dv_results_dict[image], **delf_results_dict[image], **lire_results_dict[image], **dir_results_dict[image], **crow_results_dict[image]}
    print("results_dict :: ", results_dict)

    # Converting the results to a pickle file.
    with open(OUT_FILE, "wb") as f:
        pickle.dump(results_dict, f)

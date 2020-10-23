# imports
import pickle
import argparse
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create pickle of all the pre-computed query results.')
    parser.add_argument('-qik', default="pre_constructed_data/QIK_Captions_Pre_Results_Dict.txt", metavar='data', help='QIK captions results.', required=False)
    parser.add_argument('-qik_objects_8', default="pre_constructed_data/QIK_Objects_8_Pre_Results_Dict.txt", metavar='data', help='QIK objects results with object detection threshold set as 0.8.', required=False)
    parser.add_argument('-qik_objects_9', default="pre_constructed_data/QIK_Objects_9_Pre_Results_Dict.txt", metavar='data', help='QIK objects results with object detection threshold set as 0.9.', required=False)
    parser.add_argument('-frcnn', default="pre_constructed_data/Deep_Vision_Pre_Results_Dict.txt", metavar='data', help='FR-CNN Results.', required=False)
    parser.add_argument('-dir', default="pre_constructed_data/DIR_Pre_Results_Dict.txt", metavar='data', help='DIR Results.', required=False)
    parser.add_argument('-delf', default="pre_constructed_data/DELF_Pre_Results_Dict.txt", metavar='data', help='DELF Results.', required=False)
    parser.add_argument('-lire', default="pre_constructed_data/LIRE_Pre_Results_Dict.txt", metavar='data', help='LIRE Results.', required=False)
    parser.add_argument('-crow', default="pre_constructed_data/Crow_Pre_Results_Dict.txt", metavar='data', help='CroW Results.', required=False)
    parser.add_argument('-out', default="pre_constructed_data/15K_Results.pkl", metavar='data', help='Pickled results file.', required=False)
    args = parser.parse_args()

    # Combined Results Dictionary.
    results_dict = {}

    # Iterating over QIK Results.
    qik_results_dict = {}
    results = open(args.qik, "r")
    for result in results:
        qik_results_dict[result.split("::")[0].strip()] = json.loads(result.split("::")[1].replace("'",'"'))
    print("qik_results_dict :: ", qik_results_dict)

    # Iterating over QIK Objects (0.8) Results.
    qik_objects_8_results_dict = {}
    results = open(args.qik_objects_8, "r")
    for result in results:
        qik_objects_8_results_dict[result.split("::")[0].strip()] = json.loads(result.split("::")[1].replace("'", '"'))
    print("qik_objects_8_results_dict :: ", qik_objects_8_results_dict)

    # Iterating over QIK Objects (0.9) Results.
    qik_objects_9_results_dict = {}
    results = open(args.qik_objects_9, "r")
    for result in results:
        qik_objects_9_results_dict[result.split("::")[0].strip()] = json.loads(result.split("::")[1].replace("'", '"'))
    print("qik_objects_9_results_dict :: ", qik_objects_9_results_dict)

    # Iterating over DeepVision Results.
    dv_results_dict = {}
    results = open(args.frcnn, "r")
    for result in results:
        dv_results_dict[result.split("::")[0].strip()] = json.loads(result.split("::")[1].replace("'", '"'))
    print("dv_results_dict :: ", dv_results_dict)

    # Iterating over DELF Results.
    delf_results_dict = {}
    results = open(args.delf, "r")
    for result in results:
        delf_results_dict[result.split("::")[0].strip()] = json.loads(result.split("::")[1].replace("'", '"'))
    print("delf_results_dict :: ", delf_results_dict)

    # Iterating over LIRE Results.
    lire_results_dict = {}
    results = open(args.lire, "r")
    for result in results:
        lire_results_dict[result.split("::")[0].strip()] = json.loads(result.split("::")[1].replace("'", '"'))
    print("lire_results_dict :: ", lire_results_dict)

    # Iterating over DIR Results.
    dir_results_dict = {}
    results = open(args.dir, "r")
    for result in results:
        dir_results_dict[result.split("::")[0].strip()] = json.loads(result.split("::")[1].replace("'", '"'))
    print("dir_results_dict :: ", dir_results_dict)

    # Iterating over CROW Results.
    crow_results_dict = {}
    results = open(args.crow, "r")
    for result in results:
        crow_results_dict[result.split("::")[0].strip()] = json.loads(result.split("::")[1].replace("'", '"'))
    print("crow_results_dict :: ", crow_results_dict)

    # Combining all the results.
    for image in qik_results_dict:
        if image in qik_objects_8_results_dict and image in qik_objects_9_results_dict and image in dv_results_dict and image in delf_results_dict and image in lire_results_dict and image in dir_results_dict and image in crow_results_dict:
            results_dict[image] = {**qik_results_dict[image], **qik_objects_8_results_dict[image], **qik_objects_9_results_dict[image], **dv_results_dict[image], **delf_results_dict[image], **lire_results_dict[image], **dir_results_dict[image], **crow_results_dict[image]}
    print("results_dict :: ", results_dict)

    # Converting the results to a pickle file.
    with open(args.out, "wb") as f:
        pickle.dump(results_dict, f)

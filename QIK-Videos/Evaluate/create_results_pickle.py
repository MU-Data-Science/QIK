# imports
import pickle
import argparse
import json

def create_results_dict(inp_file):
    results_dict = {}
    
    results = open(inp_file, "r")
    for line in results:
        """
        Create a results dictionary
        """
        splits = line.strip().split("=")
        results_dict[splits[0]] = json.loads(splits[1].replace("'", "\""))

    return results_dict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create pickle of all the pre-computed query results.')
    parser.add_argument('-qik_scene_match', default="pre_constructed_data/QIK_Scene_Match_Pre_Results_Dict.txt", metavar='data', help='QIK video retrieval results, ranked using scene matching', required=False)
    parser.add_argument('-qik_lcs', default="pre_constructed_data/QIK_LCS_Pre_Results_Dict.txt", metavar='data', help='QIK video retrieval results, ranked using LCS', required=False)
    parser.add_argument('-qik_ted_and_lcs', default="pre_constructed_data/QIK_LCS_And_TED_Pre_Results_Dict.txt", metavar='data', help='QIK video retrieval results, ranked using LCS and TED', required=False)
    parser.add_argument('-qik_scene_match_ted_and_lcs', default="pre_constructed_data/QIK_Scene_Match_LCS_And_TED_Pre_Results_Dict.txt", metavar='data', help='QIK video retrieval results, ranked using scene matching, LCS and TED', required=False)
    parser.add_argument('-dns_0', default="pre_constructed_data/DnS_0_Pre_Results_Dict.txt", metavar='data', help='DnS results, with re-ranking percentage set a 0', required=False) # This is the results from a hijacked execution
    parser.add_argument('-dns_0_5', default="pre_constructed_data/DnS_0_5_Pre_Results_Dict.txt", metavar='data', help='DnS results, with re-ranking percentage set a 0.5', required=False)
    parser.add_argument('-dns_1', default="pre_constructed_data/DnS_1_Pre_Results_Dict.txt", metavar='data', help='DnS results, with re-ranking percentage set a 1', required=False)
    parser.add_argument('-csq', default="pre_constructed_data/CSQ_Pre_Results_Dict.txt", metavar='data', help='CSQ results', required=False)
    parser.add_argument('-out', default="pre_constructed_data/Video_Retrieval_Results.pkl", metavar='data', help='Pickled results file.', required=False)
    args = parser.parse_args()

    # Create the results dictionary
    qik_scene_match_results_dict = create_results_dict(args.qik_scene_match)
    qik_lcs_results_dict = create_results_dict(args.qik_lcs)
    qik_ted_and_lcs_results_dict = create_results_dict(args.qik_ted_and_lcs)
    qik_scene_match_ted_and_lcs_results_dict = create_results_dict(args.qik_scene_match_ted_and_lcs)
    dns_0_results_dict = create_results_dict(args.dns_0)
    dns_0_5_results_dict = create_results_dict(args.dns_0_5)
    dns_1_results_dict = create_results_dict(args.dns_1)    
    csq_results_dict = create_results_dict(args.csq)
    
    # Combining all the results.
    results_dict = {}
    for video in qik_ted_and_lcs_results_dict:
        try:
            results_dict[video] = {**qik_scene_match_results_dict[video], **qik_lcs_results_dict[video], **qik_ted_and_lcs_results_dict[video], **qik_scene_match_ted_and_lcs_results_dict[video], **dns_0_results_dict[video], **dns_0_5_results_dict[video], **dns_1_results_dict[video], **csq_results_dict[video]}
        except:
            print("Video not present")

    # Converting the results to a pickle file.
    with open(args.out, "wb") as f:
        pickle.dump(results_dict, f)
    

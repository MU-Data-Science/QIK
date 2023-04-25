#Independent Functionality Test.
from util import sentence_similarity
from util import parse_show_tree
from util import rank_calculator
import subprocess

# Search Query
searchQuery = "A man walking in a blue jacket"

# Query SOLR to fetch the candidates.
caption1 = "A man standing in a red jacket"
caption2 = "A man walking in a blue jacket"
caption3 = "A man walking in a jacket"
caption4 = "A black dog chasing a blue cat"
captionsLst = [caption1, caption2, caption3, caption4]

rankingInp = []
captionRanksDict = {}

tfdict = sentence_similarity.getSimilarityScore(searchQuery, captionsLst)

queryParseTree = parse_show_tree.dependencyParser(searchQuery)
queryDepTree = parse_show_tree.parseSentence(searchQuery)

for caption in captionsLst:
    print("Computing for caption :: ", caption)
    captionParseTree = parse_show_tree.dependencyParser(caption)
    aptShell = "python -m apted -t " + queryParseTree + " " + captionParseTree
    parseTED = subprocess.check_output(['bash', '-c', aptShell]).decode('utf-8').rstrip()
    print("Parse Tree TED :: ", parseTED)

    captionDepTree = parse_show_tree.parseSentence(caption)
    aptShell = "python -m apted -t " + queryDepTree + " " + captionDepTree
    depTED = subprocess.check_output(['bash', '-c', aptShell]).decode('utf-8').rstrip()
    print("Dep Tree TED :: ", depTED)

    similarityScore = tfdict.get(caption)
    print("Similarity Score :: ", similarityScore)

    rank = "0 qid:1 1:" + parseTED + " 2:" + depTED + " 3:" + str(similarityScore)
    print(rank)
    rankingInp.append(rank)

ranks = rank_calculator.getRanking(rankingInp)
for rank, caption in zip(ranks, captionsLst):
    #captionRanksDict.add(ranks[i], captionsLst[i])
    print(caption)
    captionRanksDict[caption] = rank[0]

sortedCaptionRanksDict = sorted(tfdict.items(), key=lambda kv: kv[1], reverse=True)
print(sortedCaptionRanksDict)


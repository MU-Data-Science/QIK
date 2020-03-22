from nltk.parse.stanford import StanfordParser
from nltk.parse.stanford import StanfordDependencyParser

def printSentence(sentList):
    for line in sentList:
        return line

def parseSentence(inputSentence):
    parser=StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
    parsedSentence=parser.raw_parse(inputSentence)
    sent = printSentence(parsedSentence)
    ret = str(sent).replace("\n","").replace('    ', "").replace("(","{").replace(")","}").replace(" {", "{")
    return ret

def dependencyParser(inputSentence):
    depParser = StanfordDependencyParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
    depSentence = [parse.tree() for parse in depParser.raw_parse(inputSentence)]
    sent = printSentence(depSentence)
    ret = str(sent).replace("\n","").replace("  ","").replace(" (","{").replace("(","{").replace(")","}").replace(" ","{").replace("}{","}}{") + "}"
    return ret

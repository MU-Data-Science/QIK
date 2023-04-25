from nltk.parse.stanford import StanfordParser
from nltk.parse.stanford import StanfordDependencyParser

is_init = False
parser = None
depParser = None

def init():
    global is_init, parser, depParser

    if not is_init:
        parser = StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
        depParser = StanfordDependencyParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
        is_init = True

def printSentence(sentList):
    for line in sentList:
        return line

def parseSentence(inputSentence):
    parsedSentence=parser.raw_parse(inputSentence)
    sent = printSentence(parsedSentence)
    ret = str(sent).replace("\n","").replace('    ', "").replace("(","{").replace(")","}").replace(" {", "{")
    return ret

def dependencyParser(inputSentence):
    depSentence = [parse.tree() for parse in depParser.raw_parse(inputSentence)]
    sent = printSentence(depSentence)
    ret = str(sent).replace("\n","").replace("  ","").replace(" (","{").replace("(","{").replace(")","}").replace(" ","{").replace("}{","}}{") + "}"
    return ret

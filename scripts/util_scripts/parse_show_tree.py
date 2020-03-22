#!/usr/local/bin/python

import sys
import nltk
from nltk.parse.stanford import StanfordParser
from nltk.parse.stanford import StanfordDependencyParser
from nltk.parse.stanford import StanfordNeuralDependencyParser 
from nltk.tag.stanford import StanfordPOSTagger, StanfordNERTagger 
from nltk.tokenize.stanford import StanfordTokenizer
from nltk.tree import Tree

def printSentence(sentList):
	for line in sentList:
		print(line)
		line.draw()

def parseSentence(inputSentence):
	parser=StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
	parsedSentence=parser.raw_parse(inputSentence)
	printSentence(parsedSentence)

def dependencyParser(inputSentence):
	depParser = StanfordDependencyParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
	depSentence = [parse.tree() for parse in depParser.raw_parse(inputSentence)]
	printSentence(depSentence)

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print("parse_show_tree <sentence_to_parse>")
	else:
		print("Generating the parse tree....")
		parseSentence(sys.argv[1])
		print("Generating the dependency tree....")
		dependencyParser(sys.argv[1])

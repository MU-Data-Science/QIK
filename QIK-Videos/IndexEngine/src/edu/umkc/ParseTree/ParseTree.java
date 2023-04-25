package edu.umkc.ParseTree;

import edu.stanford.nlp.pipeline.CoreDocument;
import edu.stanford.nlp.pipeline.CoreSentence;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import java.util.Properties;
import edu.stanford.nlp.trees.*;

public class ParseTree {

	private static ParseTree instance = null;
	private static Properties props = new Properties();
	private static final Logger logger = LogManager.getLogger(ParseTree.class.getName());

	private ParseTree() {

	}

	public static ParseTree getInstance() {
		if(instance == null) {
			instance = new ParseTree();
			try {
				// Setting up the pipeline properties.
				props.setProperty("annotators", "tokenize,ssplit,pos,lemma,parse,depparse");
				props.setProperty("coref.algorithm", "neural");
			} catch (Exception e) {
				e.printStackTrace();
			}

		}
		return instance;
	}

	public String getParseTree(String input) {
		// Building the pipeline.
		StanfordCoreNLP pipeline = new StanfordCoreNLP(props);

		// Creating a CoreDocument object
		CoreDocument document = new CoreDocument(input.replaceAll(" , ", " "));

		// Annotating the document
		pipeline.annotate(document);

		// Taking the input query
		CoreSentence sentence = document.sentences().get(0);

		// Constructing the constituency parse for the input query.
		Tree constituencyParse = sentence.constituencyParse();
		logger.debug("ParseTree :: getParseTree :: " + constituencyParse);

		return String.valueOf(constituencyParse);
	}

}

package edu.umkc.ParseTree;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathFactory;

import edu.stanford.nlp.pipeline.CoreDocument;
import edu.stanford.nlp.pipeline.CoreSentence;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.w3c.dom.Document;

import com.google.gson.Gson;

import java.util.Properties;

import edu.stanford.nlp.trees.*;
import edu.umkc.Bean.CaptionBean;
import edu.umkc.Bean.SolrBean;
import edu.umkc.Constants.Constants;
import edu.umkc.Util.CommonUtil;
import edu.umkc.Util.XMLUtil;


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
		 
	public static void uploadData(String inp) {
		logger.debug("ParseTree :: uploadData :: Start");
		Gson gson = new Gson();
		CaptionBean captionBean = gson.fromJson(inp, CaptionBean.class);
		
		CommonUtil.getInstance().uploadParseTree(ParseTree.getInstance().getParseTree(captionBean.getCap1_cap()), captionBean.getKey(), captionBean.getCap1_cap(), captionBean.getCap1_p(), captionBean.getCap1_dep_tree(),captionBean.getLat(), captionBean.getLng(), captionBean.getObjects());

		// Ignoring the other captions.
		//CommonUtil.getInstance().uploadParseTree(ParseTree.getInstance().getParseTree(captionBean.getCap2_cap()), captionBean.getKey(), captionBean.getCap2_cap(), captionBean.getCap2_p());
		//CommonUtil.getInstance().uploadParseTree(ParseTree.getInstance().getParseTree(captionBean.getCap3_cap()), captionBean.getKey(), captionBean.getCap3_cap(), captionBean.getCap3_p());

		logger.debug("ParseTree :: uploadData :: End");
	}
	
	public static String retrieve(String query) {
		Gson gson = new Gson();

		// Obtaining the parse tree for the query.
		String parseTree = String.valueOf(ParseTree.getInstance().getParseTree(query));

		// Converting the parse tree to an XML.
		Document doc = CommonUtil.getInstance().convertStringToDocument(XMLUtil.convertToXML(parseTree));

		// Create XPathFactory object.
		XPathFactory xpathFactory = XPathFactory.newInstance();
		// Create XPath object.
		XPath xpath = xpathFactory.newXPath();

		// Fetching the noun and verb.
		List<String> nounLst = XMLUtil.getInstance().executeXPathQuery(doc, Constants.NOUN_QUERY_STRING);
		List<String> verbLst = XMLUtil.getInstance().executeXPathQuery(doc, Constants.VERB_QUERY_STRING);

		Map<String, Object> map = new HashMap<String, Object>();
		map.put("noun", nounLst);
		map.put("verb", verbLst);
		map.put("tree", parseTree);

		List<SolrBean> outputLst = CommonUtil.getInstance().querySolr();
		map.put("output", outputLst);

		if(map != null) {
			logger.debug("ParseTree :: retrieve :: Returning map :: " + map);
			return gson.toJson(map);
		}
		return null;
	}

}

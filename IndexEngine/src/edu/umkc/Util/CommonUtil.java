package edu.umkc.Util;

import java.io.StringReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.common.SolrInputDocument;
import org.apache.solr.common.params.CommonParams;
import org.w3c.dom.Document;
import org.xml.sax.InputSource;

import edu.umkc.Bean.SolrBean;
import edu.umkc.Constants.Constants;

public class CommonUtil {

	public static CommonUtil instance = null;
	private static final Logger logger = LogManager.getLogger(CommonUtil.class.getName());


	private CommonUtil() {

	}

	public static CommonUtil getInstance() {
		if (instance == null) {
			instance = new CommonUtil();
		}
		return instance;
	}

	public static Document convertStringToDocument(String xmlStr) {
		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
		DocumentBuilder builder;
		try {
			builder = factory.newDocumentBuilder();
			Document doc = builder.parse(new InputSource(new StringReader(xmlStr)));
			return doc;
		} catch (Exception e) {
			e.printStackTrace();
		}
		return null;
	}

	public static void uploadParseTree(String parseTree, String key, String caption, String prob, String depTree,String lat, String lng, String[] objects) {
		logger.debug("CommonUtil :: uploadParseTree :: Start");

		SolrInputDocument solrDoc = new SolrInputDocument();
		solrDoc.addField("caption",  caption); 
		solrDoc.addField("prob",  prob); 
		solrDoc.addField("key",  key); 
		solrDoc.addField("parseTree",  parseTree.replaceAll("\\(", "{").replaceAll("\\)", "}"));
		solrDoc.addField("depTree",  depTree);
		solrDoc.addField("lat",  lat);
		solrDoc.addField("lng",  lng);
		if(objects != null && objects.length > 0) {
			solrDoc.addField("objects", Arrays.asList(objects));
		}

		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
		factory.setNamespaceAware(true);
		try {
			// Converting the parse tree to an XML.
			String xmlString = XMLUtil.convertToXML(String.valueOf(parseTree));
			logger.debug("CommonUtil :: uploadParseTree :: xmlString :: " + xmlString);

			// Converting to an XML.
			Document doc = convertStringToDocument(xmlString);

			//Extracting nouns from the XML
			List<String> nounLst = XMLUtil.getInstance().executeXPathQuery(doc, Constants.NOUN_QUERY_STRING);
			logger.debug("CommonUtil :: uploadParseTree :: nounLst :: " + nounLst);

			//Extracting verbs from the XML
			List<String> verbLst = XMLUtil.getInstance().executeXPathQuery(doc, Constants.VERB_QUERY_STRING);
			logger.debug("CommonUtil :: uploadParseTree :: verbLst :: " + verbLst);

			solrDoc.addField("noun",  nounLst != null ? nounLst.toString() : null);
			solrDoc.addField("verb",  verbLst != null ? verbLst.toString() : null);

			// Uploading to SOLR
			logger.debug("CommonUtil :: uploadParseTree :: Uploading to SOLR");
			SolrUtil.getInstance().uploadToSolr(solrDoc);

		} catch (Exception e) {
			logger.error("CommonUtil :: uploadParseTree :: Exception encountered");
			e.printStackTrace();
		}

		logger.debug("CommonUtil :: uploadParseTree :: End");
	}
	
	public static List<SolrBean> querySolr() {
		try {
			SolrQuery query = new SolrQuery();
			query.set(CommonParams.Q, "*:*");
			query.setRows(Constants.SOLR_FETCH_LIMIT);
			return SolrUtil.getInstance().querySolr(query);
		} catch (Exception e) {
			e.printStackTrace();
		}
		return null;
	}
	
}

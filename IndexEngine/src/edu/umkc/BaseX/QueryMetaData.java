package edu.umkc.BaseX;

import com.google.gson.Gson;
import edu.umkc.Bean.ObjectsBean;
import edu.umkc.Bean.QIKResultBean;
import edu.umkc.Constants.Constants;
import edu.umkc.Embedding.FetchNearestNeighbour;
import edu.umkc.Embedding.WordBloomFilter;
import edu.umkc.ParseTree.ParseTree;
import edu.umkc.Util.CommonUtil;
import edu.umkc.Util.XMLUtil;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.w3c.dom.Document;

import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathFactory;
import java.net.ConnectException;
import java.util.*;

public class QueryMetaData {

    private static QueryMetaData instance = null;
    private static ParseTree parseTreeInst = ParseTree.getInstance();
    private static final Logger logger = LogManager.getLogger(QueryMetaData.class.getName());


    private QueryMetaData() {

    }

    public static QueryMetaData getInstance() {
        if (instance == null) {
            instance = new QueryMetaData();
        }

        return instance;
    }

    public static String queryObejcts(String objects) {
        logger.debug("QueryMetaData :: queryObejcts :: Start");

        String retLst = null;
        Gson gson = new Gson();

        ObjectsBean objs = gson.fromJson(objects, ObjectsBean.class);

        // Forming an xpath expression with the objects.
        String xpath = XMLUtil.getInstance().getXPathQueryForObjects(objs.getObjects());

        //Querying BaseX
        List<QIKResultBean> resultList = convertResultToQIKResults(queryBaseX("//DOC[" + xpath + "]"));

        // Converting the result to a json.
        if (resultList != null && !resultList.isEmpty()) {
            retLst = gson.toJson(resultList);
            logger.debug("QueryMetaData :: queryObejcts :: resultList :: " + retLst);
        }

        return retLst;
    }

    public static String queryData(String query) {
        Long time = System.currentTimeMillis();
        List<QIKResultBean> resultList = new ArrayList<QIKResultBean>();
        Gson gson = new Gson();
        String retLst = null;

        // Getting the Parse Tree.
        String parseTree = String.valueOf(parseTreeInst.getParseTree(query));
        logger.debug("QueryMetaData :: queryData :: parseTree :: " + parseTree);

        // Converting the Parse Tree to an XML Representation with unique elements.
        String xmlString = XMLUtil.convertToUniqueXML(String.valueOf(parseTree));
        logger.debug("QueryMetaData :: queryData :: xmlString :: " + xmlString);
        Document doc = CommonUtil.getInstance().convertStringToDocument(xmlString);

        //Converting the XML to a min XML.
        Document minXMLDoc = XMLUtil.getInstance().convertToUniqueMinXML(doc);

        //Constructing the complete XPath
        String xpathExpr = XMLUtil.getInstance().GenerateBasicXPath(minXMLDoc);
        logger.debug("QueryMetaData :: queryData :: xpathExpr :: " + xpathExpr);

        // Generating an optimized xpath
        String optimizedXPath = XMLUtil.getInstance().GenerateOptimizedXPath(xpathExpr);
        logger.debug("QueryMetaData :: queryData :: optimizedXPath :: " + optimizedXPath);

        // Querying BaseX.
        List<String> rstLst = queryBaseX("//DOC[" + optimizedXPath + "]");

        // Adding to the result list.
        resultList.addAll(convertResultToQIKResults(rstLst));

        // Converting the result to a json.
        if (resultList != null && !resultList.isEmpty()) {
            retLst = gson.toJson(resultList);
            logger.debug("QueryMetaData :: queryData :: resultList :: " + retLst);
        }

        logger.debug("QueryMetaData :: queryData :: Time taken for querying :: " + (System.currentTimeMillis() - time));
        return retLst;
    }

    public static List<String> queryBaseX(String xpath) {
        List<String> retLst = new ArrayList<String>();
        // Unlimited retries (Limit in production).
        while (true) {
            // Create session
            try (BaseXClient session = new BaseXClient(Constants.BASEX_HOST, Constants.BASEX_PORT, Constants.BASEX_USER, Constants.BASEX_PWD)) {

                // Open DB
                session.execute("open " + Constants.DB_NAME);

                // Run query on database
                try (BaseXClient.Query query = session.query(xpath)) {
                    // loop through all results
                    while (query.more()) {
                        retLst.add(query.next());
                    }
                    // print query info
                    logger.debug("QueryMetaData :: queryData :: query.info() :: " + query.info());
                }
                return retLst;
            } catch (ConnectException e) {
                logger.debug("QueryMetaData :: queryData :: Connection refused. Retrying");
            } catch (Exception e) {
                e.printStackTrace();
                return null;
            }
        }
    }

    public static List<QIKResultBean> convertResultToQIKResults(List<String> queryResults) {
        List<QIKResultBean> resultList = new ArrayList<QIKResultBean>();

        for (String rst : queryResults) {
            logger.debug("QueryMetaData :: convertResultToQIKResults :: rstLst :: " + rst);

            // Converting the result xml string to a document.
            Document rdoc = CommonUtil.getInstance().convertStringToDocument(rst);

            // Create XPathFactory object.
            XPathFactory xpathFactory = XPathFactory.newInstance();

            // Create XPath object.
            XPath xpathFact = xpathFactory.newXPath();

            // Fetching the file, caption and the dependency tree.
            String fileURL = XMLUtil.getInstance().executeXPathQuery(rdoc, Constants.FILE_QUERY_STRING).get(0);
            String caption = XMLUtil.getInstance().executeXPathQuery(rdoc, Constants.CAPTION_QUERY_STRING).get(0);
            String depTree = XMLUtil.getInstance().executeXPathQuery(rdoc, Constants.DEP_TREE_QUERY_STRING).get(0);
            String parTree = XMLUtil.getInstance().executeXPathQuery(rdoc, Constants.PARSE_TREE_QUERY_STRING).get(0);

            // Adding them to QIKResultBean to form the JSON.
            QIKResultBean res = new QIKResultBean();
            res.setFileURL(fileURL);
            res.setCaption(caption);
            res.setDepTree(depTree);
            res.setParseTree(parTree);

            // Adding to the result list.
            resultList.add(res);
        }

        logger.debug("QueryMetaData :: convertResultToQIKResults :: resultList :: " + resultList);
        return resultList;
    }

    public static String querySimilarImages(String query) {
        logger.debug("QueryMetaData :: querySimilarImages :: Start");
        String retStr = null;
        Gson gson = new Gson();

        // Getting the Parse Tree.
        String parseTree = String.valueOf(ParseTree.getInstance().getParseTree(query));

        // Converting Parse Tree to unique XML representation
        String uniqueXMLString = XMLUtil.convertToUniqueXML(String.valueOf(parseTree));
        Document uniqueDoc = CommonUtil.getInstance().convertStringToDocument(uniqueXMLString);

        //Converting the XML to a min XML.
        Document uniqueMinXMLDoc = XMLUtil.getInstance().convertToUniqueMinXML(uniqueDoc);

        //Constructing the complete XPath
        String xpathExpr = XMLUtil.getInstance().GenerateBasicXPath(uniqueMinXMLDoc);

        // Generating an optimized xpath
        String optimizedXPath = XMLUtil.getInstance().GenerateOptimizedXPath(xpathExpr);
        logger.debug("QueryMetaData :: querySimilarImages :: optimizedXPath :: " + optimizedXPath);

        // Standard Parse Tree to XML representation.
        String xmlStr = XMLUtil.convertToXML(String.valueOf(parseTree));
        Document doc = CommonUtil.getInstance().convertStringToDocument(xmlStr);

        //Converting the XML to a min XML.
        Document minXMLDoc = XMLUtil.getInstance().convertToMinXML(doc);

        // Extracting all nouns.
        List<String> nounOutput = XMLUtil.getInstance().executeXPathQuery(minXMLDoc, Constants.NOUN_QUERY_STRING);
        logger.debug("QueryMetaData :: querySimilarImages :: nounOutput :: " + nounOutput);

        // Constructing a xpath list replacing the word with the similar words.
        Map<String, String> resultMap = querySimilarImages(query, optimizedXPath, nounOutput, Constants.NOUN);

        // Extracting all verbs.
        List<String> verbOutput = XMLUtil.getInstance().executeXPathQuery(minXMLDoc, Constants.VERB_QUERY_STRING);
        logger.debug("QueryMetaData :: querySimilarImages :: verbOutput :: " + verbOutput);

        // Adding to the xpath list replacing the word with the similar words.
        resultMap.putAll(querySimilarImages(query, optimizedXPath, verbOutput, Constants.VERB));

        logger.debug("QueryMetaData :: querySimilarImages :: resultMap :: " + resultMap);

        // Converting the result to a json.
        if (resultMap != null && !resultMap.isEmpty()) {
            retStr = gson.toJson(resultMap);
            logger.debug("QueryMetaData :: querySimilarImages :: retStr :: " + retStr);
        }

        return retStr;
    }

    public static Map<String, String> querySimilarImages(String caption, String optimizedXPath, List<String> wordLst, String pos) {
        logger.debug("QueryMetaData :: querySimilarImages :: Start with pos :: " + pos);
        Map<String, String> retMap = new LinkedHashMap<String, String>();

        for(String word: wordLst) {
            // Get the closest neighbours of a word.
            List<String> nearestNeighbours = FetchNearestNeighbour.getInstance().getNearestNeighbours(word, Constants.EMBED_K);
            if(nearestNeighbours != null) {
                // Iterating over the k neighbours.
                for(String similarWord: nearestNeighbours) {
                    // Verify if the new word is present in the corpus, using a bloom filter.
                    if(WordBloomFilter.getInstance().isPresent(similarWord, pos)) {
                        String newOptimizedXPath = new String(optimizedXPath).replaceAll("\\b" + word + "\\b", similarWord);
                        System.out.println("QueryMetaData :: querySimilarImages :: newOptimizedXPath :: " + newOptimizedXPath);
                        //Querying to check if there are candidates.
                        List<String> imgList = QueryMetaData.getInstance().queryBaseX("//FILE[" + newOptimizedXPath + "]/text()");
                        if(imgList != null && imgList.size() > 0) {
                            for(String image : imgList) {
                                retMap.put(image, new String(caption).replaceAll("\\b" + word + "\\b", similarWord));
                            }
                        }
                    }
                }
            }
        }

        logger.debug("QueryMetaData :: querySimilarImages :: retMap :: " + retMap);
        return retMap;
    }

    public static List<String> getSimilarXPath(String query) {
        logger.debug("QueryMetaData :: getSimilarXPath :: Start");
        String retStr = null;
        Gson gson = new Gson();

        // Getting the Parse Tree.
        String parseTree = String.valueOf(ParseTree.getInstance().getParseTree(query));

        // Converting Parse Tree to unique XML representation
        String uniqueXMLString = XMLUtil.convertToUniqueXML(String.valueOf(parseTree));
        Document uniqueDoc = CommonUtil.getInstance().convertStringToDocument(uniqueXMLString);

        //Converting the XML to a min XML.
        Document uniqueMinXMLDoc = XMLUtil.getInstance().convertToUniqueMinXML(uniqueDoc);

        //Constructing the complete XPath
        String xpathExpr = XMLUtil.getInstance().GenerateBasicXPath(uniqueMinXMLDoc);

        // Generating an optimized xpath
        String optimizedXPath = XMLUtil.getInstance().GenerateOptimizedXPath(xpathExpr);
        logger.debug("QueryMetaData :: getSimilarXPath :: optimizedXPath :: " + optimizedXPath);

        // Standard Parse Tree to XML representation.
        String xmlStr = XMLUtil.convertToXML(String.valueOf(parseTree));
        Document doc = CommonUtil.getInstance().convertStringToDocument(xmlStr);

        //Converting the XML to a min XML.
        Document minXMLDoc = XMLUtil.getInstance().convertToMinXML(doc);

        // Extracting all nouns.
        List<String> nounOutput = XMLUtil.getInstance().executeXPathQuery(minXMLDoc, Constants.NOUN_QUERY_STRING);
        logger.debug("QueryMetaData :: getSimilarXPath :: nounOutput :: " + nounOutput);

        // Constructing a xpath list replacing the word with the similar words.
        List<String> resultLst = getSimilarXPath(optimizedXPath, nounOutput, Constants.NOUN);

        return resultLst;
    }


    public static List<String> getSimilarXPath(String optimizedXPath, List<String> wordLst, String pos) {
        logger.debug("QueryMetaData :: getSimilarXPath :: Start with pos :: " + pos);
        List<String> retLst = new ArrayList<String>();

        for(String word: wordLst) {
            // Get the closest neighbours of a word.
            List<String> nearestNeighbours = FetchNearestNeighbour.getInstance().getNearestNeighbours(word, Constants.EMBED_K);
            if(nearestNeighbours != null) {
                // Iterating over the k neighbours.
                for(String similarWord: nearestNeighbours) {
                    // Verify if the new word is present in the corpus, using a bloom filter.
                    if(WordBloomFilter.getInstance().isPresent(similarWord, pos)) {
                        String newOptimizedXPath = new String(optimizedXPath).replaceAll("\\b" + word + "\\b", similarWord);
                        System.out.println("newOptimizedXPath :: " + newOptimizedXPath);
                        //Querying to check if there are candidates.
                        List<String> imgList = QueryMetaData.getInstance().queryBaseX("//FILE[" + newOptimizedXPath + "]/text()");
                        if(imgList != null && imgList.size() > 0) {
                            retLst.add(newOptimizedXPath);
                        }
                    }
                }
            }
        }

        logger.debug("QueryMetaData :: getSimilarXPath :: retLst :: " + retLst);
        return retLst;
    }
}
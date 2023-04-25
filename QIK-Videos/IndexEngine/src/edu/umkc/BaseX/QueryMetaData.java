package edu.umkc.BaseX;

import com.google.gson.Gson;
import edu.umkc.Bean.CaptionBean;
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
    private static final Logger logger = LogManager.getLogger(QueryMetaData.class.getName());


    private QueryMetaData() {

    }

    public static QueryMetaData getInstance() {
        if (instance == null) {
            instance = new QueryMetaData();
        }

        return instance;
    }

    public static String queryData(String inp) {
        logger.debug("QueryMetaData :: queryData :: Start");

        String resMap = null;
        Long time = System.currentTimeMillis();
        Map<Integer, List<String>> rstMap = new LinkedHashMap<Integer, List<String>>();
        Map<Integer, List<QIKResultBean>> resultMap = new LinkedHashMap<Integer, List<QIKResultBean>>();
        Gson gson = new Gson();

        // Converting the input json.
        CaptionBean captionBean = gson.fromJson(inp, CaptionBean.class);

        // Video scene captions.
        String[] captionsArr = captionBean.getCaptionsArr();

        // Obtaining the Parse Tree representations of the captions.
        List<String> parseTreeLst = new ArrayList<String>();
        for(String caption: captionsArr) {
            // Getting the Parse Tree.
            String parseTree = String.valueOf(ParseTree.getInstance().getParseTree(caption));
            logger.debug("QueryMetaData :: queryData :: parseTree :: " + parseTree);

            // Adding it to the buffer.
            parseTreeLst.add(parseTree);
        }

        /* Commenting all scene querying for search speedup - Start
        // Initializing a StringBuffer and adding the root.
        StringBuffer sb = new StringBuffer();
        sb.append("(VIDEO_ROOT (CAP_ROOT ");

        // Adding the parse tress of the captions.
        for(String parseTree: parseTreeLst) {
            sb.append(parseTree);
        }

        // Closing the root node.
        sb.append("))");

        // Querying on the complete XML.
        rstLst = queryXML(sb.toString());
        Commenting all scene querying for search speedup - End */

        // Querying on the individual parse trees.
        for(int i=0; i<parseTreeLst.size(); i++) {
            StringBuffer indSB = new StringBuffer();
            indSB.append(parseTreeLst.get(i));
            rstMap.put(i+1, queryXML(indSB.toString()));
        }

        // Adding to the result list.
        resultMap = convertResultToQIKResults(rstMap);

        // Converting the result to a json.
        if (resultMap != null && !resultMap.isEmpty()) {
            resMap = CommonUtil.getInstance().convertToJsonString(resultMap);
        }

        // Adding the query parse trees to the return map to prevent recomputing them for ranking
        String parseTreeLstStr = new Gson().toJson(parseTreeLst);
        parseTreeLstStr = parseTreeLstStr.replaceAll("\\(", "{").replaceAll("\\)", "}");
        String retMap = "{\"queryResults\": " + resMap + ", \"querySceneParseTrees\": " + parseTreeLstStr + "}";

        logger.debug("QueryMetaData :: queryData :: Time taken for querying :: " + (System.currentTimeMillis() - time));
        return retMap;
    }

    public static List<String> queryXML(String xml) {
        logger.debug("QueryMetaData :: queryXML :: Start");

        // Converting the XML string to a document.
        String capXMLString = XMLUtil.convertToUniqueXML(String.valueOf(xml));
        Document doc = CommonUtil.getInstance().convertStringToDocument(capXMLString);

        //Converting the XML to a min XML.
        Document minXML = XMLUtil.getInstance().convertToUniqueMinXML(doc);

        //Constructing the complete XPath
        String xpathExpr = XMLUtil.getInstance().GenerateBasicXPath(minXML);

        // Generating an optimized xpath
        String optimizedXPath = XMLUtil.getInstance().GenerateOptimizedXPath(xpathExpr);
        logger.debug("QueryMetaData :: queryData :: optimizedXPath :: " + optimizedXPath);

        // Querying BaseX.
        List<String> rstLst = queryBaseX("//DOC[" + optimizedXPath + "]");
        // logger.debug("QueryMetaData :: queryXML :: rstLst :: " + rstLst);

        return rstLst;
    }

    public static List<String> queryBaseX(String xpath) {
        List<String> retLst = new ArrayList<String>();
        // Unlimited retries (Limit in production).
        while (true) {
            // Create session
            try (BaseXClient session = new BaseXClient(Constants.BASEX_HOST, Constants.BASEX_PORT, Constants.BASEX_USER, Constants.BASEX_PWD)) {

                // Open DB
                session.execute("open " + Constants.DB_NAME);

                // Initializing flag to handle Errors
                boolean isException = false;
                boolean hasProcessesed = false;

                // Run query on database
                try (BaseXClient.Query query = session.query(xpath)) {
                    // loop through all results
                    while (query.more()) {
                        retLst.add(query.next());
                    }
                    // print query info
                    logger.debug("QueryMetaData :: queryData :: query.info() :: " + query.info());
                    hasProcessesed = true;
                } catch (Exception e) {
                    logger.debug("QueryMetaData :: queryData :: Exception encountered");
                    e.printStackTrace();
                    isException = true;
                } finally {
                    logger.debug("QueryMetaData :: queryData :: isException :: " + isException + " :: hasProcessesed :: " + hasProcessesed);
                    if(!isException && !hasProcessesed) {
                        throw new Exception("GC/Memory issues encountered while processing");
                    }
                }
                return retLst;
            } catch (ConnectException e) {
                logger.debug("QueryMetaData :: queryData :: Connection refused. Retrying");
            } catch (Exception e) {
                return retLst;
            }
            return retLst;
        }
    }

    public static Map<Integer, List<QIKResultBean>> convertResultToQIKResults(Map<Integer, List<String>> queryResults) {
        Map<Integer, List<QIKResultBean>> resultMap = new LinkedHashMap<Integer, List<QIKResultBean>>();

        for (Integer idx : queryResults.keySet()) {
            for(String rst: queryResults.get(idx)) {
                // Converting the result xml string to a document.
                Document rdoc = CommonUtil.getInstance().convertStringToDocument(rst);

                // Create XPathFactory object.
                XPathFactory xpathFactory = XPathFactory.newInstance();

                // Create XPath object.
                XPath xpathFact = xpathFactory.newXPath();

                // Fetching the scene
                List<String> fileURLLst = XMLUtil.getInstance().executeXPathQuery(rdoc, Constants.FILE_QUERY_STRING);
                if(fileURLLst == null || fileURLLst.isEmpty() || fileURLLst.size() == 0) {
                    logger.error("QueryMetaData :: convertResultToQIKResults :: irregular document :: Skipping");
                    continue;
                }
                String fileURL = fileURLLst.get(0);
                logger.debug("QueryMetaData :: convertResultToQIKResults :: fileURL :: " + fileURL);

                // Obtaining the id for that scene
                String sceneId = XMLUtil.getInstance().executeXPathQuery(rdoc, Constants.ID_QUERY_STRING).get(0);

                // Obtaining the caption for that scene
                String caption = XMLUtil.getInstance().executeXPathQuery(rdoc, Constants.CAPTION_QUERY_STRING).get(0);

                // Obtaining the dependency tree for that scene caption.
                String depTree = XMLUtil.getInstance().executeXPathQuery(rdoc, Constants.DEP_TREE_QUERY_STRING).get(0);

                // Obtaining the dependency tree for that scene caption.
                String parseTree = XMLUtil.getInstance().executeXPathQuery(rdoc, Constants.PARSE_TREE_QUERY_STRING).get(0);

                // Adding them to QIKResultBean to form the JSON.
                QIKResultBean res = new QIKResultBean();
                res.setFileURL(fileURL);
                res.setSceneId(sceneId);
                res.setCaption(caption);
                res.setDepTree(depTree);
                res.setParseTree(parseTree);

                // Adding to the result map.
                if(resultMap.containsKey(idx)) {
                    List<QIKResultBean> resultList = resultMap.get(idx);
                    resultList.add(res);
                    resultMap.put(idx, resultList);
                } else {
                    List<QIKResultBean> resultList = new ArrayList<QIKResultBean>();
                    resultList.add(res);
                    resultMap.put(idx, resultList);
                }
            }
        }

        logger.debug("QueryMetaData :: convertResultToQIKResults :: resultMap :: " + resultMap);
        return resultMap;
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
package edu.umkc.BaseX;

import com.google.gson.Gson;
import edu.umkc.Bean.CaptionBean;
import edu.umkc.Constants.Constants;
import edu.umkc.ParseTree.ParseTree;
import edu.umkc.Util.CommonUtil;
import edu.umkc.Util.XMLUtil;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.w3c.dom.Document;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.util.List;

public class UploadMetaData {

    private static UploadMetaData instance = null;
    private static final CommonUtil comUtil = CommonUtil.getInstance();
    private static final XMLUtil xmlUtil = XMLUtil.getInstance();
    private static final Logger logger = LogManager.getLogger(UploadMetaData.class.getName());


    private UploadMetaData() {

    }

    public static UploadMetaData getInstance() {
        if (instance == null) {
            instance = new UploadMetaData();
        }
        return instance;
    }

    public static void uploadData(String inp) {
        logger.debug("UploadMetaData :: uploadData :: Start");
        // inp : Captions generated from im2txt
        Gson gson = new Gson();
        CaptionBean captionBean = gson.fromJson(inp, CaptionBean.class);

        // Create the session
        try(BaseXClient session = new BaseXClient(Constants.BASEX_HOST, Constants.BASEX_PORT, Constants.BASEX_USER, Constants.BASEX_PWD)) {
            //XML File name
            String xml = System.currentTimeMillis() + "_";

            // Opening the DB
            session.execute("open " + Constants.DB_NAME);

            // Caption 1:
            // Forming the XML data for upload and converting it to bytes.
            InputStream stream1 = new ByteArrayInputStream(formXMLString(captionBean.getKey(), captionBean.getCap1_cap(), ParseTree.getInstance().getParseTree(captionBean.getCap1_cap()), captionBean.getCap1_dep_tree(), captionBean.getLat(), captionBean.getLng(), captionBean.getObjects()).getBytes());

            // To add a document
            session.add(xml + "_1.xml", stream1);

            /* Ignoring the other captions.
            // Caption 2:
            // Forming the XML data for upload and converting it to bytes.
            InputStream stream2 = new ByteArrayInputStream(formXMLString(captionBean.getKey(), captionBean.getCap2_cap()).getBytes());

            // To add a document
            session.add(xml + "_2.xml", stream2);

            // Caption 3:
            // Forming the XML data for upload and converting it to bytes.
            InputStream stream3 = new ByteArrayInputStream(formXMLString(captionBean.getKey(), captionBean.getCap3_cap()).getBytes());

            // To add a document
            session.add(xml + "_3.xml", stream3);
            */
        } catch (Exception e) {
            e.printStackTrace();
            logger.debug("UploadMetaData :: uploadData :: Exception encountered while pushing to BaseX :: " + e);
        }
        logger.debug("UploadMetaData :: uploadData :: End");
    }

    public static String formXMLString(String filePath, String caption, String parseTree, String depTree, String lat, String lng, String[] objects) {
        logger.debug("UploadMetaData :: formXMLString :: Start");
        // Obtaining the parse tree for the Caption.
        String tree = ParseTree.getInstance().getParseTree(caption);

        // Converting the parse tree to an XML.
        String xmlString = xmlUtil.convertToXML(String.valueOf(tree));
        logger.debug("UploadMetaData :: formXMLString :: xmlString :: " + xmlString);
        Document doc = comUtil.convertStringToDocument(xmlString);

        // Extracting nouns from the XML
        List<String> nounLst = xmlUtil.executeXPathQuery(doc, Constants.NOUN_QUERY_STRING);

        // Extracting verbs from the XML
        List<String> verbLst = xmlUtil.executeXPathQuery(doc, Constants.VERB_QUERY_STRING);

        //Converting the XML to a min XML.
        Document minXML = xmlUtil.convertToMinXML(doc);
        String minXMLStr = xmlUtil.convertXMLDocToString(minXML);

        return formXMLString(filePath, caption, minXMLStr, nounLst, verbLst, parseTree, depTree, lat, lng, objects);

    }

    private static String formXMLString(String filePath, String caption, String minXMLStr, List<String> nounLst, List<String> verbLst, String parseTree, String depTree, String lat, String lng, String[] objects) {
        logger.debug("UploadMetaData :: formXMLString :: Start");
        StringBuffer sb = new StringBuffer();

        // Adding Header
        sb.append("<DOC>");

        // Adding the image path
        sb.append("<FILE>" + filePath + "</FILE>");

        // Adding the caption
        sb.append("<CAPTION>" + caption + "</CAPTION>");

        // Adding the parse XML
        sb.append(minXMLStr);

        // Adding noun list
        sb.append("<NOUN_LIST>");
        for(String noun : nounLst) {
            sb.append("<NOUN VALUE='" + noun +"'/>");
        }
        sb.append("</NOUN_LIST>");

        // Adding verb list
        sb.append("<VERB_LIST>");
        for(String verb : verbLst) {
            sb.append("<VERB VALUE='" + verb +"'/>");
        }
        sb.append("</VERB_LIST>");

        // Adding the parse tree
        sb.append("<PARSE_TREE>" + parseTree.replaceAll("\\(", "{").replaceAll("\\)", "}") + "</PARSE_TREE>");

        // Adding the dependency tree
        sb.append("<DEP_TREE>" + depTree + "</DEP_TREE>");

        // Adding latitude and longitudes.
        sb.append("<GEO_TAG>");
        sb.append("<LAT>"+ lat +"</LAT>");
        sb.append("<LNG>"+ lng +"</LNG>");
        sb.append("</GEO_TAG>");

        // Adding objects detected.
        if(objects != null && objects.length > 0) {
            sb.append("<OBJECTS>");
            for(String object : objects) {
                sb.append("<OBJECT>" + object + "</OBJECT>");
            }
            sb.append("</OBJECTS>");
        }

        sb.append("</DOC>");

        logger.debug("UploadMetaData :: formXMLString :: XML to Upload :: " + sb.toString());
        return sb.toString();
    }
}
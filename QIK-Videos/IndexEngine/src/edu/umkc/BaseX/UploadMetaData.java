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

            // Forming the XML data for upload and converting it to bytes.
            InputStream stream1 = new ByteArrayInputStream(formXMLString(captionBean.getKey(), captionBean.getSceneId(), captionBean.getCaptionsArr()[0], captionBean.getDepTreesArr()[0], ParseTree.getInstance().getParseTree(captionBean.getCaptionsArr()[0])).getBytes());

            // To add a document
            session.add(xml + "_1.xml", stream1);

        } catch (Exception e) {
            e.printStackTrace();
            logger.debug("UploadMetaData :: uploadData :: Exception encountered while pushing to BaseX :: " + e);
        }
        logger.debug("UploadMetaData :: uploadData :: End");
    }

    public static String formXMLString(String filePath, String sceneId,  String caption, String depTree, String parseTree) {
        logger.debug("UploadMetaData :: formXMLString :: Start");
        // Obtaining the parse tree for the Caption.
        String tree = ParseTree.getInstance().getParseTree(caption);

        // Converting the parse tree to an XML.
        String xmlString = xmlUtil.convertToXML(String.valueOf(tree));
        logger.debug("UploadMetaData :: formXMLString :: xmlString :: " + xmlString);
        Document doc = comUtil.convertStringToDocument(xmlString);

        //Converting the XML to a min XML.
        Document minXML = xmlUtil.convertToMinXML(doc);
        String minXMLStr = xmlUtil.convertXMLDocToString(minXML);

        return formXMLString(filePath, sceneId, caption, minXMLStr, depTree, parseTree);

    }

    private static String formXMLString(String filePath, String sceneId, String caption, String minXMLStr, String depTree, String parseTree) {
        logger.debug("UploadMetaData :: formXMLString :: Start");
        StringBuffer sb = new StringBuffer();

        // Adding Header
        sb.append("<DOC>");

        // Adding the image path
        sb.append("<FILE id=\"" + sceneId + "\">" + filePath + "</FILE>");

        // Adding the captions
        sb.append("<CAPTION_LIST>");
        sb.append("<CAPTION>" + caption + "</CAPTION>");
        sb.append("</CAPTION_LIST>");

        // Adding the root to the video captions.
        sb.append("<SCENE_ROOT>");
        sb.append(minXMLStr);
        sb.append("</SCENE_ROOT>");

        // Adding the parse trees
        sb.append("<PARSE_TREE>" + parseTree.replaceAll("\\(", "{").replaceAll("\\)", "}") + "</PARSE_TREE>");

        // Adding the dependency trees
        sb.append("<DEP_TREE_LIST>");
        sb.append("<DEP_TREE>" + depTree + "</DEP_TREE>");
        sb.append("</DEP_TREE_LIST>");

        sb.append("</DOC>");

        logger.debug("UploadMetaData :: formXMLString :: XML to Upload :: " + sb.toString());
        return sb.toString();
    }
}
package edu.umkc.Validate;

import edu.umkc.ParseTree.ParseTree;
import edu.umkc.Util.CommonUtil;
import edu.umkc.Util.XMLUtil;
import org.w3c.dom.Document;

import java.util.List;

public class VideoInputXPathValidator {
    public static void main(String[] args) {
        try {
            // Video scene captions
            String[] captionsArr = {"a little boy that is eating some kind of food", "a little girl eating a piece of pizza", "a little boy sitting in a high chair eating pizza"};

            // Initializing a StringBuffer and adding the root.
            StringBuffer sb = new StringBuffer();
            sb.append("(VIDEO_ROOT (CAP_ROOT ");

            for(String caption: captionsArr) {
                // Getting the Parse Tree.
                String parseTree = String.valueOf(ParseTree.getInstance().getParseTree(caption));
                System.out.println("parseTree :: " + parseTree);

                // Adding it to the buffer.
                sb.append(parseTree);
            }

            // Closing the root node.
            sb.append("))");

            // Converting the XML string to a document.
            String capXMLString = XMLUtil.convertToUniqueXML(String.valueOf(sb.toString()));
            Document doc = CommonUtil.getInstance().convertStringToDocument(capXMLString);

            //Converting the XML to a min XML.
            Document minXML = XMLUtil.getInstance().convertToUniqueMinXML(doc);

            //Constructing the complete XPath
            String xpathExpr = XMLUtil.getInstance().GenerateBasicXPath(minXML);

            // Generating an optimized xpath
            String optimizedXPath = XMLUtil.getInstance().GenerateOptimizedXPath(xpathExpr);
            System.out.println("VideoInputXPathValidator :: main :: optimizedXPath :: " + optimizedXPath);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

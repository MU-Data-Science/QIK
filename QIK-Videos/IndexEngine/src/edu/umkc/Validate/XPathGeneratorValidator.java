package edu.umkc.Validate;

import edu.umkc.ParseTree.ParseTree;
import edu.umkc.Util.CommonUtil;
import edu.umkc.Util.XMLUtil;
import org.w3c.dom.Document;

import java.util.List;
import java.util.Set;

public class XPathGeneratorValidator {
    public static void main(String[] args) {

        // Input Query.
        String query = "a man standing on a tennis court holding a racquet";

        // Getting the Parse Tree.
        String parseTree = String.valueOf(ParseTree.getInstance().getParseTree(query));

        // Converting the XML string to a document.
        String capXMLString = XMLUtil.convertToUniqueXML(parseTree);
        Document doc = CommonUtil.getInstance().convertStringToDocument(capXMLString);

        //Converting the XML to a min XML.
        Document minXML = XMLUtil.getInstance().convertToUniqueMinXML(doc);

        //Constructing the complete XPath
        String xpathExpr = XMLUtil.getInstance().GenerateBasicXPath(minXML);

        // Generating an optimized xpath
        String optimizedXPath = XMLUtil.getInstance().GenerateOptimizedXPath(xpathExpr);

        System.out.println(optimizedXPath);
    }

}

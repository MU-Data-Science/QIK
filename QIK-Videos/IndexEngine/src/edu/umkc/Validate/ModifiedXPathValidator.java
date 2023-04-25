package edu.umkc.Validate;

import edu.umkc.ParseTree.ParseTree;
import edu.umkc.Util.CommonUtil;
import edu.umkc.Util.XMLUtil;
import org.w3c.dom.Document;

public class ModifiedXPathValidator {
    public static void main(String[] args) {

        // Input Query.
        String query = "a young boy kicking a soccer ball on a field";

        // Getting the Parse Tree.
        String parseTree = String.valueOf(ParseTree.getInstance().getParseTree(query));

        // Standard Parse Tree to XML representation.
        String xmlStr = XMLUtil.convertToXML(String.valueOf(parseTree));
        System.out.println("XML :: " + xmlStr);

        // Converting the Parse Tree to an XML Representation with unique elements.
        String xmlString = XMLUtil.convertToUniqueXML(String.valueOf(parseTree));
        System.out.println("Unique XML :: " + xmlString);
        Document doc = CommonUtil.getInstance().convertStringToDocument(xmlString);

        //Converting the XML to a min XML.
        Document minXMLDoc = XMLUtil.getInstance().convertToUniqueMinXML(doc);

        //Constructing the complete XPath
        String xpathExpr = XMLUtil.getInstance().GenerateBasicXPath(minXMLDoc);
        System.out.println("xpathExpr :: " + xpathExpr);

        // Generating an optimized xpath
        String optimizedXPath = XMLUtil.getInstance().GenerateOptimizedXPath(xpathExpr);
        System.out.println(optimizedXPath);
    }

}

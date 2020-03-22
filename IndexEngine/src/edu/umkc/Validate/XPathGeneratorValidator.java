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
        String query = "a large elephant walking through a lush green field";

        // Getting the Parse Tree.
        String parseTree = String.valueOf(ParseTree.getInstance().getParseTree(query));

        // Converting the Parse Tree to an XML Representation.
        String xmlString = XMLUtil.convertToXML(String.valueOf(parseTree));
        System.out.println("XML :: " + xmlString);
        Document doc = CommonUtil.getInstance().convertStringToDocument(xmlString);

        //Converting the XML to a min XML.
        Document minXMLDoc = XMLUtil.getInstance().convertToMinXML(doc);

        // Forming the min XPath expressions.
        Set<String> minXpathLst = XMLUtil.getInstance().getMinXpath(minXMLDoc);

        System.out.println(minXpathLst);
    }

}

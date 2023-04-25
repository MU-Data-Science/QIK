package edu.umkc.Validate;

import edu.umkc.ParseTree.ParseTree;
import edu.umkc.Util.CommonUtil;
import edu.umkc.Util.XMLUtil;
import org.w3c.dom.Document;

import java.util.Set;

public class ValidatorUtil {

    public static void main(String[] args) {
        for(int i=0; i<args.length; i++) {
            // Obtaing the caption from the input
            String caption = args[i];
            System.out.println("ValidatorUtil :: main :: Caption :: " + caption);

            // Getting the Parse Tree.
            String parseTree = String.valueOf(ParseTree.getInstance().getParseTree(caption));
            System.out.println("ValidatorUtil :: main :: parseTree :: " + parseTree);

            // Converting the Parse Tree to an XML Representation.
            String xmlString = XMLUtil.convertToXML(parseTree);
            System.out.println("ValidatorUtil :: main :: xmlString :: " + xmlString);

            //Converting the XML to a min XML.
            Document doc = CommonUtil.getInstance().convertStringToDocument(xmlString);
            Document minXMLDoc = XMLUtil.getInstance().convertToMinXML(doc);

            // Forming the min XPath expressions.
            Set<String> minXpathLst = XMLUtil.getInstance().getMinXpath(minXMLDoc);
            System.out.println("ValidatorUtil :: main :: minXpathLst :: " + minXpathLst);

        }
    }
}
package edu.umkc.Validate;

import edu.umkc.ParseTree.ParseTree;
import edu.umkc.Util.CommonUtil;
import edu.umkc.Util.XMLUtil;
import org.w3c.dom.Document;

import java.util.List;

public class XPathValidator {
    public static void main(String[] args) {
        try {
            // Candidate Query
            String query = "A man and a dog are chasing a white cat";

            // Getting the Parse Tree.
            String parseTree = String.valueOf(ParseTree.getInstance().getParseTree(query));

            // Converting the Parse Tree to an XML Representation.
            String xmlString = XMLUtil.convertToXML(String.valueOf(parseTree));
            Document doc = CommonUtil.getInstance().convertStringToDocument(xmlString);

            //Converting the XML to a min XML.
            Document minXML = XMLUtil.getInstance().convertToMinXML(doc);

            String xpathQ = "//NN[text()='cat']/following::VBG[text()='chasing']/following::NN[text()='dog']";

            List<String> output = XMLUtil.getInstance().executeXPathQuery(doc, xpathQ);

            if(output != null && !output.isEmpty()) {
                System.out.println("Matches");
            } else {
                System.out.println("Doesnot match");
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

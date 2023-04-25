package edu.umkc.Util;

import edu.umkc.Constants.Constants;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.w3c.dom.traversal.DocumentTraversal;
import org.w3c.dom.traversal.NodeFilter;
import org.w3c.dom.traversal.TreeWalker;
import org.w3c.dom.Element;

import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import javax.xml.xpath.*;
import java.io.StringWriter;
import java.util.*;
import java.util.regex.Pattern;

public class XMLUtil {
    public static XMLUtil instance;
    private static final Logger logger = LogManager.getLogger(XMLUtil.class.getName());
    private static final Pattern emptyValueTag = Pattern.compile("\\s*<\\w+/>");
    private static final Pattern emptyTagMultiLine = Pattern.compile("\\s*<\\w+>\n*\\s*</\\w+>");

    private XMLUtil() {

    }

    public static XMLUtil getInstance() {
        if (instance == null) {
            instance = new XMLUtil();
        }
        return instance;
    }

    /*
     * Eg:
     * Sentence : A cat being chased by a dog
     * Input : (ROOT (FRAG (NP (DT A) (NN cat)) (S (VP (VBG being) (VP (VBD chased) (PP (IN by) (NP (DT a) (NN dog))))))))
     * Output : <ROOT><FRAG><NP><DT>A</DT><NN>cat</NN></NP><S><VP><VBG>being</VBG><VP><VBD>chased</VBD><PP><IN>by</IN><NP><DT>a</DT><NN>dog</NN></NP></PP></VP></VP></S></FRAG></ROOT>
     */
    public static String convertToXML(String input) {
        input = input.replace(") (", ")(").replaceAll("[^a-zA-Z0-9 ()]", "");
        StringBuffer xmlBuffer = new StringBuffer();
        StringBuffer wordBuffer = new StringBuffer();
        Stack<String> stack = new Stack<String>();
        boolean start = false;
        for (int i = 0; i < input.length(); i++) {
            if (start && input.charAt(i) != '(') {
                wordBuffer.append(input.charAt(i));
            }
            if (input.charAt(i) == '(') {
                xmlBuffer.append("<");
                start = true;
                continue;
            } else if (input.charAt(i) == ' ') {
                xmlBuffer.append(">");
                String word = wordBuffer.toString().trim();
                stack.push(word);
                wordBuffer = new StringBuffer();
                start = false;
                continue;
            } else if (input.charAt(i) == ')') {
                String word = stack.pop();
                xmlBuffer.append("</" + word + ">");
            } else {
                xmlBuffer.append(input.charAt(i));
            }
        }
        return xmlBuffer.toString();
    }

    public static List<String> executeXPathQuery(Document doc, String query) {
        // Creating XPathFactory object
        XPathFactory xpathFactory = XPathFactory.newInstance();

        // Creating XPath object
        XPath xpath = xpathFactory.newXPath();

        List<String> list = new ArrayList<>();
        try {
            // Executing the Xpath query.
            XPathExpression expr = xpath.compile(query);
            NodeList nodes = (NodeList) expr.evaluate(doc, XPathConstants.NODESET);
            for (int i = 0; i < nodes.getLength(); i++) {
                //Adding the contents to the list.
                list.add(nodes.item(i).getTextContent());
            }
        } catch (XPathExpressionException e) {
            e.printStackTrace();
        }
        return list;
    }

    public static String executeStringQuery(Document doc, String query) {
        // Creating XPathFactory object
        XPathFactory xpathFactory = XPathFactory.newInstance();

        // Creating XPath object
        XPath xpath = xpathFactory.newXPath();

        List<String> list = new ArrayList<>();
        try {
            // Executing the Xpath query.
            XPathExpression expr = xpath.compile(query);
            return (String) expr.evaluate(doc, XPathConstants.STRING);
        } catch (XPathExpressionException e) {
            e.printStackTrace();
        }
        return null;
    }

    public static Boolean executeBooleanQuery(Document doc, String query) {
        // Creating XPathFactory object
        XPathFactory xpathFactory = XPathFactory.newInstance();

        // Creating XPath object
        XPath xpath = xpathFactory.newXPath();

        List<String> list = new ArrayList<>();
        try {
            // Executing the Xpath query.
            XPathExpression expr = xpath.compile(query);
            Boolean value = (Boolean) expr.evaluate(doc, XPathConstants.BOOLEAN);
            return value;
        } catch (XPathExpressionException e) {
            e.printStackTrace();
        }
        return false;
    }

    public static String convertToUniqueXML(String input) {
        input = input.replace(") (", ")(").replaceAll("[^a-zA-Z0-9 ()]", "");
        StringBuffer xmlBuffer = new StringBuffer();
        StringBuffer wordBuffer = new StringBuffer();
        Stack<String> stack = new Stack<String>();
        boolean start = false;
        int j = 0;
        for (int i = 0; i < input.length(); i++) {
            if (start && input.charAt(i) != '(') {
                wordBuffer.append(input.charAt(i));
            }
            if (input.charAt(i) == '(') {
                xmlBuffer.append("<");
                start = true;
                continue;
            } else if (input.charAt(i) == ' ') {
                xmlBuffer.append("_" + j);
                xmlBuffer.append(">");
                String word = wordBuffer.toString().trim() + "_" + j;
                stack.push(word);
                wordBuffer = new StringBuffer();
                j += 1;
                start = false;
                continue;
            } else if (input.charAt(i) == ')') {
                String word = stack.pop();
                xmlBuffer.append("</" + word + ">");
            } else {
                xmlBuffer.append(input.charAt(i));
            }
        }
        return xmlBuffer.toString();
    }

    public static Document convertToMinXML(Document doc) {
        try {
            // Finding the unnecessary nodes.
            XPath xPath = XPathFactory.newInstance().newXPath();
            XPathExpression xExpress = xPath.compile(Constants.NECC_DETAILS_QUERY_STRING);
            NodeList nodeList = (NodeList) xExpress.evaluate(doc.getDocumentElement(), XPathConstants.NODESET);

            // Removing the unnecessary nodes.
            for (int index = 0; index < nodeList.getLength(); index++) {
                Node node = nodeList.item(index);
                removeNode(node);
            }

            // Hack to remove empty nodes - Start.
            String tempXML = XMLUtil.convertXMLDocToString(doc);
            tempXML = emptyValueTag.matcher(tempXML).replaceAll("");

            while (tempXML.length() != (tempXML = emptyTagMultiLine.matcher(tempXML).replaceAll("")).length()) {
            }

            doc = CommonUtil.getInstance().convertStringToDocument(tempXML);
            // Hack to remove empty nodes - End
        } catch (Exception e) {
            e.printStackTrace();
        }

        return doc;
    }

    public static Document convertToUniqueMinXML(Document doc) {
        try {
            // Finding the unnecessary nodes.
            XPath xPath = XPathFactory.newInstance().newXPath();
            XPathExpression xExpress = xPath.compile(Constants.UNIQUE_NECC_DETAILS_QUERY_STRING);
            NodeList nodeList = (NodeList) xExpress.evaluate(doc.getDocumentElement(), XPathConstants.NODESET);

            // Removing the unnecessary nodes.
            for (int index = 0; index < nodeList.getLength(); index++) {
                Node node = nodeList.item(index);
                removeNode(node);
            }

            // Hack to remove empty nodes - Start.
            String tempXML = XMLUtil.convertXMLDocToString(doc);
            tempXML = emptyValueTag.matcher(tempXML).replaceAll("");

            while (tempXML.length() != (tempXML = emptyTagMultiLine.matcher(tempXML).replaceAll("")).length()) {
            }

            doc = CommonUtil.getInstance().convertStringToDocument(tempXML);
            // Hack to remove empty nodes - End
        } catch (Exception e) {
            e.printStackTrace();
        }

        return doc;
    }

    // To remove nodes from the XML. Ref :: https://stackoverflow.com/questions/27978151/how-to-remove-unwanted-tags-from-xml
    public static void removeNode(Node node) {
        if (node != null) {
            while (node.hasChildNodes()) {
                removeNode(node.getFirstChild());
            }

            Node parent = node.getParentNode();
            if (parent != null) {
                parent.removeChild(node);
                NodeList childNodes = parent.getChildNodes();
                if (childNodes.getLength() > 0) {
                    List<Node> lstTextNodes = new ArrayList<Node>(childNodes.getLength());
                    for (int index = 0; index < childNodes.getLength(); index++) {
                        Node childNode = childNodes.item(index);
                        if (childNode.getNodeType() == Node.TEXT_NODE) {
                            lstTextNodes.add(childNode);
                        }
                    }
                    for (Node txtNodes : lstTextNodes) {
                        removeNode(txtNodes);
                    }
                }
            }
        }
    }

    public static Set<String> getMinXpath(Document doc) {
        // Get the nouns and the verbs from the document.
        List<String> nounLst = XMLUtil.getInstance().executeXPathQuery(doc, Constants.NOUN_QUERY_STRING);
        List<String> verbLst = XMLUtil.getInstance().executeXPathQuery(doc, Constants.VERB_QUERY_STRING);

        // Removing nouns preceding a preposition. (For eg: a group of people, a bunch of animals)
        List<String> prepLst = new ArrayList<String>();
        if(nounLst != null && !nounLst.isEmpty() && verbLst != null && !verbLst.isEmpty()) {
            for(String sub : nounLst) {
                for(String obj : nounLst) {
                    String subtag = XMLUtil.getInstance().executeStringQuery(doc, "name(//*[text()='"+ sub +"'])");
                    String objtag = XMLUtil.getInstance().executeStringQuery(doc, "name(//*[text()='"+ obj +"'])");
                    String xpathQ = "//" + subtag + "[text()='" + sub + "']/following::IN/following::" + objtag + "[text()='" + obj + "']/following::VBG";
                    logger.debug("Printing xpathQ :: " + xpathQ);
                    if(XMLUtil.getInstance().executeBooleanQuery(doc, xpathQ)) {
                        prepLst.add(obj);
                    }

                    xpathQ = "//VBG/following::" + subtag + "[text()='" + sub + "']/following::IN/following::" + objtag + "[text()='" + obj + "']";
                    logger.debug("Printing xpathQ :: " + xpathQ);
                    if(XMLUtil.getInstance().executeBooleanQuery(doc, xpathQ)) {
                        prepLst.add(sub);
                    }
                }
            }
        }
        nounLst.removeAll(prepLst);

        logger.debug("XMLUtil :: getMinXpath :: nounLst :: " + nounLst);
        logger.debug("XMLUtil :: getMinXpath :: verbLst :: " + verbLst);

        // Form the min XPath expressions.
        Set<String> minXpathLst = new HashSet<String>();
        if(nounLst != null && !nounLst.isEmpty() && verbLst != null && !verbLst.isEmpty()) {
            for(String sub : nounLst) {
                for(String action : verbLst) {
                    for(String obj : nounLst) {
                        String subtag = XMLUtil.getInstance().executeStringQuery(doc, "name(//*[text()='"+ sub +"'])");
                        String actiontag = XMLUtil.getInstance().executeStringQuery(doc, "name(//*[text()='"+ action +"'])");
                        String objtag = XMLUtil.getInstance().executeStringQuery(doc, "name(//*[text()='"+ obj +"'])");
                        String xpathQ = "//" + subtag + "[text()='" + sub + "']/following::" + actiontag + "[text()='"+ action + "']/following::" + objtag + "[text()='" + obj + "']";
                        logger.debug("Printing xpathQ :: " + xpathQ);
                        if(XMLUtil.getInstance().executeBooleanQuery(doc, xpathQ)) {
                            minXpathLst.add(xpathQ);
                        }
                    }
                }
            }

            if(minXpathLst == null || minXpathLst.isEmpty()) {
                // Indicates that they are not in the form Subject Action Subject. Thus checking for Subject Action.
                for(String sub : nounLst) {
                    for (String action : verbLst) {
                        for (String obj : nounLst) {
                            String subtag = XMLUtil.getInstance().executeStringQuery(doc, "name(//*[text()='"+ sub +"'])");
                            String actiontag = XMLUtil.getInstance().executeStringQuery(doc, "name(//*[text()='"+ action +"'])");
                            String xpathQ = "//" + subtag + "[text()='" + sub + "']/following::" + actiontag + "[text()='"+ action + "']";
                            if(XMLUtil.getInstance().executeBooleanQuery(doc, xpathQ)) {
                                minXpathLst.add(xpathQ);
                            } else {
                                // Checking for Action Object.
                                xpathQ = "//" + actiontag + "[text()='"+ action + "']/following::" + subtag + "[text()='" + sub + "']";
                                if(XMLUtil.getInstance().executeBooleanQuery(doc, xpathQ)) {
                                    minXpathLst.add(xpathQ);
                                }
                            }
                        }
                    }
                }
            }
        } else if (nounLst != null && !nounLst.isEmpty()) { // Performing a keyword based search.
            StringBuffer xpathQ = null;
            for (String sub : nounLst) {
                String subtag = XMLUtil.getInstance().executeStringQuery(doc, "name(//*[text()='"+ sub +"'])");
                if(xpathQ == null) {
                    xpathQ = new StringBuffer();
                    xpathQ.append("//" + subtag + "[text()='" + sub + "']");
                } else {
                    xpathQ.append(" and //" + subtag + "[text()='" + sub + "']");
                }
            }
            minXpathLst.add(xpathQ.toString());
        }

        logger.debug("XMLUtil :: getMinXpath :: minXpathLst :: " + minXpathLst);
        return minXpathLst;
    }

    public static String convertXMLDocToString(Document doc) {
        try {
            TransformerFactory tf = TransformerFactory.newInstance();
            Transformer transformer = tf.newTransformer();
            transformer.setOutputProperty(OutputKeys.OMIT_XML_DECLARATION, "yes");
            StringWriter writer = new StringWriter();
            transformer.transform(new DOMSource(doc), new StreamResult(writer));
            String output = writer.getBuffer().toString().replaceAll("\n|\r", "");
            return output;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

    public static String getXPathQueryForObjects(String[] objects) {
        if(objects == null || objects.length == 0) {
            logger.error("XMLUtil :: getXPathQueryForObjects :: No objects in the list.");
            return null;
        }
        StringBuffer sb = new StringBuffer();
        sb.append("//FILE[");//FILE[//OBJECT[text()='person'] and //OBJECT[text()='wave']]"
        for(int i=0; i<objects.length -1; i++) {
            sb.append("//OBJECT[text()='" + objects[i] + "'] and ");
        }
        sb.append("//OBJECT[text()='" + objects[objects.length -1] + "']]");

        logger.debug("XMLUtil :: getXPathQueryForObjects :: xpath :: " + sb.toString());
        return sb.toString();

    }

    public static String GenerateBasicXPath(Document xmlDoc) {
        // Creating a DocumentTraversal object to traverse the XML.
        DocumentTraversal traversal = (DocumentTraversal) xmlDoc;
        TreeWalker walker = traversal.createTreeWalker(xmlDoc.getDocumentElement(), NodeFilter.SHOW_ELEMENT, null, true);

        // Traversing through the XML to construct a tree.
        Map<String, List<String>> tree = traverseLevel(walker, new LinkedList<String>(), walker.firstChild(), new LinkedHashMap<String, List<String>>());

        // XPath expression Buffer.
        StringBuffer sb = new StringBuffer();

        // Adding the root node.
        sb.append("/child::ROOT");
        List<String> l = new ArrayList<String>();
        l.add("ROOT_0");

        // Constructing the complete Xpathexpression.
        constructXPathQuery("ROOT_0", sb, xmlDoc, l, tree);

        String xpathExpr = sb.toString();
        logger.debug("XMLUtil :: GenerateBasicXPath :: " + xpathExpr);

        return xpathExpr;

    }

    private static final Map<String, List<String>> traverseLevel(TreeWalker walker, List<String> list, Node node, Map<String, List<String>> tree) {
        Node parent = walker.getCurrentNode();
        list.add(((Element) parent).getTagName());

        List<String> lst = new LinkedList<String>();
        for (Node n = walker.firstChild(); n != null; n = walker.nextSibling()) {
            traverseLevel(walker, lst, n, tree);
        }

        walker.setCurrentNode(parent);
        tree.put(((Element) node).getParentNode().getNodeName(), list);
        return tree;
    }

    private static void constructXPathQuery(String currentNode, StringBuffer sb,  Document xml, List<String> traversed, Map<String, List<String>> tree) {
        String previousNode = null;

        previousNode = traversed.size() >= 1 ? traversed.get(traversed.size() - 1) : null;

        //Check if current node is the child of the previous node.
        boolean isChild = false;
        for(String k : tree.keySet()) {
            List<String> lst = tree.get(k);
            if(lst.contains(currentNode) && (lst.contains(previousNode) || k.equals(previousNode))) {
                if(lst.indexOf(currentNode) == 0) {
                    isChild = true;
                }
            }
        }

        if(!traversed.contains(currentNode)) {
            if(isChild) {
                sb.append("/child::" + currentNode.split("_")[0]);
            } else {
                sb.append("/following::" + currentNode.split("_")[0]);
            }
        }

        if(!traversed.contains(currentNode)) {
            traversed.add(currentNode);
        }

        boolean isImmediateSibling = true;

        for(String k : tree.get(currentNode)) {
            if(!tree.containsKey(k)) {
                List<String> lst = tree.get(currentNode);
                if(lst.indexOf(k) == 0) {
                    sb.append("/child::" + k.split("_")[0]);
                } else {
                    if(isImmediateSibling) {
                        sb.append("/following-sibling::" + k.split("_")[0]);
                    } else {
                        sb.append("/following::" + k.split("_")[0]);
                    }
                }
                String txt = XMLUtil.executeStringQuery(xml, "//" + k+"//text()");
                sb.append("[text()='" + txt + "']") ;
            } else {
                constructXPathQuery(k, sb, xml, traversed, tree);
                isImmediateSibling = false;
            }
        }

    }

    public static String GenerateOptimizedXPath(String query) {
        StringBuffer sb = new StringBuffer();
        String leadingAxis = null; // leadingAxis ← NULL
        String[] queryContents = query.split("/");

        for(int i=1; i<queryContents.length; i++) {
            String[] contents = queryContents[i].split("::");
            String axis = contents[0];
            String node = contents[1];

            if(node.contains("text()")) { // if n has predicate p then
                if(leadingAxis != null && (leadingAxis.equals("following") || leadingAxis.equals("following-sibling"))) {
                    sb.append("following::" + node + "/"); // if leadingAxis is following then Append /following::n[p] to q′ // else if leadingAxis is following-sibling then Append /following::n[p] to q′
                } else {
                    sb.append(axis + "::" + node + "/"); // else Append /x::n[p] to q′
                }
                leadingAxis = null; // leadingAxis ← NU LL
            } else if(axis.equals("child")) { // else if x is child then
                continue; // continue
            } else if(axis.equals("following-sibling") || axis.equals("following")) { //else if x is following::sibling or following then
                leadingAxis = axis;
            } else {
                logger.debug("XMLUtil :: GenerateOptimizedXPath :: Invalid axis");
                return null;
            }
        }

        // Replace the first axis in q′ with descendant
        int fistAxis = sb.toString().indexOf("::");
        String qDash = "/descendant" + sb.toString().substring(fistAxis, sb.toString().length() - 1);

        // return q′
        logger.debug("XMLUtil :: GenerateOptimizedXPath :: qDash :: " + qDash);
        return qDash;
    }
}
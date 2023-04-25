package edu.umkc.Servlet;

import com.google.gson.Gson;
import edu.umkc.BaseX.QueryMetaData;
import edu.umkc.ParseTree.ParseTree;
import edu.umkc.Util.CommonUtil;
import edu.umkc.Util.XMLUtil;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.w3c.dom.Document;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@WebServlet("/explain")
public class ExplainServlet extends HttpServlet {
	
	private static final long serialVersionUID = 1L;
	private static final Logger logger = LogManager.getLogger(ExplainServlet.class.getName());

	@Override
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
		doWork(request, response);
	}

	@Override
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
		doWork(request, response);
	}

	protected void doWork(HttpServletRequest request, HttpServletResponse response) throws IOException {
		logger.debug("ExplainServlet :: doWork :: Start");
		response.setHeader("Access-Control-Allow-Origin", "*");

		String query = request.getParameter("query");

		Map<String, Object> explainMap = new LinkedHashMap<String, Object>();

		// Noting the executing start time.
		long time = System.currentTimeMillis();

		// Obtaining the Parse Tree.
		String parseTree = String.valueOf(ParseTree.getInstance().getParseTree(query));
		explainMap.put("Parse_Tree", parseTree);

		// Constructing the XPath query.
		String uniqueXMLString = XMLUtil.convertToUniqueXML(parseTree);
		Document uniqueDoc = CommonUtil.getInstance().convertStringToDocument(uniqueXMLString);
		Document uniqueMinXMLDoc = XMLUtil.getInstance().convertToUniqueMinXML(uniqueDoc);
		String xpathExpr = XMLUtil.getInstance().GenerateBasicXPath(uniqueMinXMLDoc);
		explainMap.put("XPath", xpathExpr);

		// Constructing the minimized XPath query.
		String optimizedXPath = XMLUtil.getInstance().GenerateOptimizedXPath(xpathExpr);
		explainMap.put("Optimized_XPath", optimizedXPath);

		// Noting the total executing time.
		long execTime = System.currentTimeMillis() - time;
		explainMap.put("Query_Exec_Time", String.valueOf(execTime));
		time = System.currentTimeMillis();

		// Getting the list of similar xpath.
		List<String> xpathLst = QueryMetaData.getInstance().getSimilarXPath(query);
		explainMap.put("Similar_XPath", xpathLst);

		// Noting the total time taken for fetching similar images.
		execTime = System.currentTimeMillis() - time;
		explainMap.put("Similar_Exec_Time", execTime);

		// Obtaining the Parse tree representation
		String xmlString = XMLUtil.convertToXML(parseTree);
		explainMap.put("XML_Representation", xmlString);

		//Converting the XML to a min XML.
		Document doc = CommonUtil.getInstance().convertStringToDocument(xmlString);
		Document minXMLDoc = XMLUtil.getInstance().convertToMinXML(doc);
		String minXMLString = CommonUtil.getInstance().convertDocumentToString(minXMLDoc);
		explainMap.put("Minimum_XML_Representation", minXMLString);

		// Converting map to a json.
		Gson json = new Gson();
		String resultJson = json.toJson(explainMap);

		PrintWriter out = response.getWriter();
		out.println(resultJson);
	}
}

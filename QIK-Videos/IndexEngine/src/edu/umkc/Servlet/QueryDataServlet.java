package edu.umkc.Servlet;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.PrintWriter;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import edu.umkc.BaseX.QueryMetaData;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

@WebServlet("/query")
public class QueryDataServlet  extends HttpServlet {
	
	private static final long serialVersionUID = 1L;
	private static final Logger logger = LogManager.getLogger(QueryDataServlet.class.getName());

	@Override
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
		doWork(request, response);
	}

	@Override
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
		logger.debug("QueryDataServlet :: doPost :: Start");
		StringBuffer sb = new StringBuffer();
		String line = null;
		try {
			BufferedReader reader = request.getReader();
			while ((line = reader.readLine()) != null) {
				sb.append(line);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}

		// Fetch the list of image URL's based on the input.
		String results = QueryMetaData.getInstance().queryData(sb.toString());

		response.getWriter().write(results);
	}

	protected void doWork(HttpServletRequest request, HttpServletResponse response) throws IOException {
		logger.debug("QueryDataServlet :: doWork :: Start");
		response.setHeader("Access-Control-Allow-Origin", "*");
		String query = request.getParameter("query");
		logger.debug("QueryDataServlet :: doWork :: query :: " + query);
		// Fetch the list of image URL's based on the input.
		String results = QueryMetaData.getInstance().queryData(query);

		PrintWriter out = response.getWriter();
		out.println(results);
	}
}

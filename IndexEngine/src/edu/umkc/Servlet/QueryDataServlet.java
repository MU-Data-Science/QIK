package edu.umkc.Servlet;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import edu.umkc.BaseX.QueryMetaData;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import edu.umkc.ParseTree.ParseTree;

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
		doWork(request, response);
	}

	protected void doWork(HttpServletRequest request, HttpServletResponse response) throws IOException {
		logger.debug("QueryDataServlet :: doWork :: Start");
		response.setHeader("Access-Control-Allow-Origin", "*");
		String query = request.getParameter("query");	

		// Fetch the list of image URL's based on the input.
		String imgList = QueryMetaData.getInstance().queryData(query);

		PrintWriter out = response.getWriter();
		out.println(imgList);
	}
}

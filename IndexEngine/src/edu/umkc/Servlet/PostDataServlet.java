package edu.umkc.Servlet;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.concurrent.BlockingQueue;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import edu.umkc.Util.DataProducer;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

@WebServlet("/postData")
public class PostDataServlet  extends HttpServlet {
	
	private static final long serialVersionUID = 1L;
	private static final Logger logger = LogManager.getLogger(PostDataServlet.class.getName());

	@Override
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
		doWork(request, response);
	}

	@Override
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
		doWork(request, response);
	}

	protected void doWork(HttpServletRequest request, HttpServletResponse response) throws IOException {
		logger.debug("PostDataServlet :: doWork :: Start");
		response.setHeader("Access-Control-Allow-Origin", "*");
		String data = request.getParameter("data");
		logger.debug("PostDataServlet :: Data :: " + data);

		// Inserting the captions to a queue.
		DataProducer.getInstance().insert(data);

		PrintWriter out = response.getWriter();
		out.println(data);
	}
}

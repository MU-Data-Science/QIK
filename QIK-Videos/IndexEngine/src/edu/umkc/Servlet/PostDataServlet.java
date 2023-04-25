package edu.umkc.Servlet;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.BlockingQueue;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.google.gson.Gson;
import edu.umkc.Constants.Constants;
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
		// Creating the desired request object.
		Enumeration<String> params = request.getParameterNames();
		Map<String, String> data = new HashMap();
		while(params.hasMoreElements()) {
			String paramName = params.nextElement();
			if(Constants.DATA.equals(paramName)) {
				continue; // Fix to handle data key from post request.
			}
			data.put(paramName, request.getParameter(paramName));
		}
		logger.debug("PostDataServlet :: doPost :: data :: " + data.toString());
		
		// Inserting the captions to a queue.
		DataProducer.getInstance().insert(data.toString());
	}

	protected void doWork(HttpServletRequest request, HttpServletResponse response) throws IOException {
		logger.debug("PostDataServlet :: doWork :: Start");
		response.setHeader("Access-Control-Allow-Origin", "*");
		String data = request.getParameter("data");
		logger.debug("PostDataServlet :: doWork :: data :: " + data);

		// Inserting the captions to a queue.
		DataProducer.getInstance().insert(data);

		PrintWriter out = response.getWriter();
		out.println(data);
	}
}

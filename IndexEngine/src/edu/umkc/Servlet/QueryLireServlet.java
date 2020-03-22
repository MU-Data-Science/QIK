package edu.umkc.Servlet;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import edu.umkc.BaseX.QueryMetaData;
import edu.umkc.Lire.QueryLire;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import edu.umkc.ParseTree.ParseTree;

@WebServlet("/queryLire")
public class QueryLireServlet extends HttpServlet {

    private static final long serialVersionUID = 1L;
    private static final Logger logger = LogManager.getLogger(QueryLireServlet.class.getName());

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        doWork(request, response);
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
        doWork(request, response);
    }

    protected void doWork(HttpServletRequest request, HttpServletResponse response) throws IOException {
        logger.debug("QueryLireServlet :: doWork :: Start");
        response.setHeader("Access-Control-Allow-Origin", "*");
        String inputImg = request.getParameter("query");   // Path for the image.
        String fetchLimit = request.getParameter("limit");   // Path for the fetch count.

        logger.debug("QueryLireServlet :: doWork :: inputImg :: " + inputImg);

        // Fetch the list of image URL's based on the input.
        List<String> results = QueryLire.getInstance().getSimilarImages(inputImg, fetchLimit);

        PrintWriter out = response.getWriter();
        out.println(results);
    }
}

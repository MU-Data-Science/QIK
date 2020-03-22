package edu.umkc.Servlet;

import java.io.IOException;
import java.io.PrintWriter;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import edu.umkc.Lire.LireIndexer;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

@WebServlet("/indexLire")
public class IndexLireServlet  extends HttpServlet {

    private static final long serialVersionUID = 1L;
    private static final Logger logger = LogManager.getLogger(IndexLireServlet.class.getName());

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        doWork(request, response);
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
        doWork(request, response);
    }

    protected void doWork(HttpServletRequest request, HttpServletResponse response) throws IOException {
        logger.debug("IndexLireServlet :: doWork :: Start");
        response.setHeader("Access-Control-Allow-Origin", "*");
        String inputDir = request.getParameter("dir");   // Path for the image.
        logger.debug("IndexLireServlet :: doWork :: inputDir :: " + inputDir);

        // Fetch the list of image URL's based on the input.
        LireIndexer.getInstance().buildLireIndex(inputDir, false);

        PrintWriter out = response.getWriter();
        out.println("Completed");
    }
}
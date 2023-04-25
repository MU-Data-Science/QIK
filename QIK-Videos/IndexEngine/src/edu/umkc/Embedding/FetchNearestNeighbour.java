package edu.umkc.Embedding;

import edu.umkc.Constants.Constants;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.*;
import java.net.URL;
import java.nio.charset.Charset;
import java.util.Arrays;
import java.util.List;

public class FetchNearestNeighbour {
    public static FetchNearestNeighbour instance = null;
    private static final Logger logger = LogManager.getLogger(FetchNearestNeighbour.class.getName());

    private FetchNearestNeighbour() {

    }

    public static FetchNearestNeighbour getInstance() {
        if (instance == null) {
            instance = new FetchNearestNeighbour();
        }
        return instance;
    }

    private static String readAll(Reader rd) throws IOException {
        StringBuilder sb = new StringBuilder();
        int cp;
        while ((cp = rd.read()) != -1) {
            sb.append((char) cp);
        }
        return sb.toString();
    }

    private static String getEmbeddingURL(String word, int k) {
        return Constants.EMBEDDING_URL + "?word=" + word + "&k=" + k;
    }

    public static List<String> getNearestNeighbours(String word, int k) {
        try(InputStream is = new URL(getEmbeddingURL(word, k)).openStream();
            BufferedReader rd = new BufferedReader(new InputStreamReader(is, Charset.forName("UTF-8")))) {
            String negihbours = readAll(rd).replaceAll("\\]", "").replaceAll("\\[", "").replaceAll("\'", "").replaceAll(" ", "");
            List<String> retList = Arrays.asList(negihbours.split(","));
            logger.debug("FetchNearestNeighbour :: getNearestNeighbours :: for the word :: " + word + " :: retList :: " + retList);
            return retList;
        } catch (Exception e) {
            logger.error("FetchNearestNeighbour :: getNearestNeighbours :: Exception encountered");
            e.printStackTrace();
        }
        return null;
    }
}

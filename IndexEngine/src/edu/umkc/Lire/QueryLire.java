package edu.umkc.Lire;

import edu.umkc.Constants.Constants;
import net.semanticmetadata.lire.builders.DocumentBuilder;
import net.semanticmetadata.lire.imageanalysis.features.global.*;
import net.semanticmetadata.lire.searchers.GenericFastImageSearcher;
import net.semanticmetadata.lire.searchers.ImageSearchHits;
import net.semanticmetadata.lire.searchers.ImageSearcher;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.store.FSDirectory;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

public class QueryLire {
    public static QueryLire instance = null;
    private static final Logger logger = LogManager.getLogger(QueryLire.class.getName());


    private QueryLire() {

    }

    public static QueryLire getInstance() {
        if(instance == null) {
            //Building the index.
            LireIndexer.getInstance();
            instance = new QueryLire();
        }
        return instance;
    }

    public static List<String> getSimilarImages(String imgPath, String fetchCount) {
        logger.debug("QueryLire :: getSimilarImages :: Start");

        List<String> retLst = new ArrayList<String>();
        // Reading the input image
        BufferedImage img = null;
        File f = new File(imgPath);
        if (f.exists()) {
            try {
                img = ImageIO.read(f);
            } catch (IOException e) {
                e.printStackTrace();
                logger.error("Excpetion encountered while trying to read the input.");
            }
        }

        try {
            // Fetching the index.
            IndexReader ir = DirectoryReader.open(FSDirectory.open(Paths.get(Constants.INDEX_PATH)));
            ImageSearcher searcher = new GenericFastImageSearcher((fetchCount != null ? Integer.parseInt(fetchCount) : Constants.LIRE_FETCH_LIMIT), CEDD.class);

            // Searching with a image file
            ImageSearchHits hits = searcher.search(img, ir);

            // searching with a Lucene document instance ...
            for (int i = 0; i < hits.length(); i++) {
                String fileName = ir.document(hits.documentID(i)).getValues(DocumentBuilder.FIELD_NAME_IDENTIFIER)[0];
                String[] fileLst = fileName.split("/");
                String file = Constants.IMAGE_URL + fileLst[fileLst.length -1]; // Coverting the file path to a server location.
                System.out.println(hits.score(i) + ": \t" + file);
                retLst.add(file);
            }
        } catch (Exception e) {
            e.printStackTrace();
            logger.debug("QueryLire :: getSimilarImages :: Exception encountered while querying LIRE index.");
        }

        return retLst;
    }

}

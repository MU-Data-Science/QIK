package edu.umkc.Lire;

import edu.umkc.Constants.Constants;
import net.semanticmetadata.lire.builders.GlobalDocumentBuilder;
import net.semanticmetadata.lire.imageanalysis.features.global.*;
import net.semanticmetadata.lire.utils.FileUtils;
import net.semanticmetadata.lire.utils.LuceneUtils;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.store.FSDirectory;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Iterator;

public class LireIndexer {
    public static LireIndexer instance = null;
    private static final Logger logger = LogManager.getLogger(LireIndexer.class.getName());

    private LireIndexer() {

    }

    public static LireIndexer getInstance() {
        if (instance == null) {
            try {
                DirectoryReader.open(FSDirectory.open(Paths.get(Constants.INDEX_PATH)));
                System.out.println("LireIndexer :: buildLireIndex :: Index present.");
            } catch (Exception e) {
                try {
                    buildLireIndex(Constants.IMAGE_DIR, true);
                } catch (Exception ex) {
                    logger.debug("LireIndexer :: getInstance :: Exception encountered while trying to index");
                }
                System.out.println("LireIndexer :: getInstance :: No prebuild index. Constructing the index.");
            }

            instance = new LireIndexer();
        }
        return instance;
    }

    public static void buildLireIndex(String imgDir, boolean create) throws IOException {
        logger.debug("LireIndexer :: buildLireIndex :: Start :: " + imgDir);

        // Getting all images from the directory and its sub directories.
        ArrayList<String> images = FileUtils.readFileLines(new File(imgDir), true);

        // Creating a CEDD document builder and indexing all files.
        GlobalDocumentBuilder globalDocumentBuilder = new GlobalDocumentBuilder(CEDD.class);

        // Creating an Lucene IndexWriter
        IndexWriter iw = LuceneUtils.createIndexWriter(Constants.INDEX_PATH, create, LuceneUtils.AnalyzerType.WhitespaceAnalyzer);

        // Iterating through images building the low level features
        for (Iterator<String> it = images.iterator(); it.hasNext(); ) {
            String imageFilePath = it.next();
            logger.debug("LireIndexer :: buildLireIndex :: Indexing " + imageFilePath);
            try {
                BufferedImage img = ImageIO.read(new FileInputStream(imageFilePath));
                Document document = globalDocumentBuilder.createDocument(img, imageFilePath);
                iw.addDocument(document);
            } catch (Exception e) {
                logger.error("LireIndexer :: buildLireIndex :: Error reading image or indexing it.");
                e.printStackTrace();
            }
        }

        // closing the IndexWriter
        iw.commit();
        LuceneUtils.closeWriter(iw);
        logger.debug("LireIndexer :: buildLireIndex :: Finished indexing.");

    }
}
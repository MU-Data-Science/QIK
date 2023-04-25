package edu.umkc.Util;

import edu.umkc.BaseX.UploadMetaData;
import edu.umkc.ParseTree.ParseTree;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.util.concurrent.BlockingQueue;

public class DataConsumer implements Runnable {
    protected BlockingQueue<String> queue;
    private static final Logger logger = LogManager.getLogger(DataConsumer.class.getName());

    public DataConsumer(BlockingQueue<String> queue) {
        this.queue = queue;
    }

    @Override
    public void run() {
        while(true) {
            try {
                // Reading the caption from the queue.
                String data = queue.take();

                // Uploading to BaseX
                UploadMetaData.getInstance().uploadData(data);

            } catch (Exception e) {
                e.printStackTrace();
                logger.error("DataConsumer :: run :: Exception encountered while reading from the queue.");
            }
        }
    }
}

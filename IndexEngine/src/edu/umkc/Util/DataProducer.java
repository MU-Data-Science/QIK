package edu.umkc.Util;

import edu.umkc.Servlet.PostDataServlet;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;

public class DataProducer {
    public static DataProducer instance = null;
    private static BlockingQueue<String> queue;
    private static final Logger logger = LogManager.getLogger(DataProducer.class.getName());

    private static void init() {
        queue = new ArrayBlockingQueue<>(100000);
        DataConsumer consumer = new DataConsumer(queue);
        new Thread(consumer).start();
    }

    private DataProducer() {

    }

    public static DataProducer getInstance() {
        if(instance == null) {
            init();
            instance = new DataProducer();
        }
        return instance;
    }

    public static void insert(String data) {
        try {
            // Adding the caption to the queue.
            queue.put(data);
        } catch (Exception e) {
            e.printStackTrace();
            logger.error("DataProducer :: doWork :: Exception encountered while adding to the queue.");
        }
    }


}

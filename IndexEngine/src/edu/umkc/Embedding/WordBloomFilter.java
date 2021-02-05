package edu.umkc.Embedding;

import com.google.common.hash.BloomFilter;
import com.google.common.hash.Funnels;
import edu.umkc.BaseX.QueryMetaData;
import edu.umkc.Constants.Constants;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.nio.charset.Charset;
import java.util.List;

public class WordBloomFilter {
    public static WordBloomFilter instance = null;
    private static final Logger logger = LogManager.getLogger(WordBloomFilter.class.getName());
    private static BloomFilter<String> nounFilter = null;
    private static BloomFilter<String> verbFilter = null;

    private WordBloomFilter() {

    }

    public static WordBloomFilter getInstance() {
        if (instance == null) {
            initBloomFilter();
            instance = new WordBloomFilter();
        }
        return instance;
    }

    private static void initBloomFilter() {
        nounFilter = BloomFilter.create(Funnels.stringFunnel(Charset.forName("UTF-8")), Constants.FILTER_SIZE);
        List<String> nounOutput = QueryMetaData.getInstance().queryBaseX(Constants.EMBED_NOUN_QUERY_STRING);
        for(String noun: nounOutput) {
            nounFilter.put(noun);
        }

        verbFilter = BloomFilter.create(Funnels.stringFunnel(Charset.forName("UTF-8")), Constants.FILTER_SIZE);
        List<String> verbOutput = QueryMetaData.getInstance().queryBaseX(Constants.EMBED_VERB_QUERY_STRING);
        for(String noun: verbOutput) {
            verbFilter.put(noun);
        }
    }

    public static BloomFilter<String> getNounFilter() {
        return nounFilter;
    }

    public static BloomFilter<String> getVerbFilter() {
        return verbFilter;
    }

    public static boolean isPresent(String word, String pos) {
        if(Constants.NOUN.equals(pos)) {
            if(nounFilter.mightContain(word)) {
                return true;
            } else {
                return false;
            }
        } else if(Constants.VERB.equals(pos)) {
            System.out.println("word :: '" + word + "'");
            if(verbFilter.mightContain(word)) {
                return true;
            } else {
                return false;
            }
        }
        return false;
    }

}

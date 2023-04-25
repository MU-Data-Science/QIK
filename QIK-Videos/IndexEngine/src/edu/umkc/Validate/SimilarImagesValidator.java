package edu.umkc.Validate;

import edu.umkc.BaseX.QueryMetaData;
import edu.umkc.Constants.Constants;
import edu.umkc.Embedding.FetchNearestNeighbour;
import edu.umkc.Embedding.WordBloomFilter;
import edu.umkc.ParseTree.ParseTree;
import edu.umkc.Util.CommonUtil;
import edu.umkc.Util.XMLUtil;
import org.w3c.dom.Document;

import java.io.*;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class SimilarImagesValidator {
    public static void main(String[] args) throws Exception {
        String query = "a truck is parked on the side of the road";

        String xpathMap = QueryMetaData.getInstance().querySimilarImages(query);

        System.out.println(xpathMap);
    }
}

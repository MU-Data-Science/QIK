package edu.umkc.Validate;

import edu.umkc.Lire.QueryLire;
import java.util.List;

public class LireValidator {
    public static void main(String[] args) {
        String inputImg = "/Users/arung/Drive/Work_Space/QIK_Space/Evaluation/Evaluation_1/LIRE/Query_2/Query.jpg";

        List<String> results = QueryLire.getInstance().getSimilarImages(inputImg, null);

        System.out.println("Results :: " + results);
    }
}

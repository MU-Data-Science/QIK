package edu.umkc.Validate;

import edu.umkc.BaseX.BaseXClient;

import java.io.*;

public class QueryBaseXValidator {
    public static void main(final String... args) {
        // Query List
        String lstQuery = "//FILE";
        String generalFetchQuery = "//FILE[//NN[text()='people'] or //NNS[text()='people']/following::VBG[text()='eating']]";
        String fetchBasedOnObjects = "//FILE[//OBJECT[text()='toilet'] and //OBJECT[text()='sink'] and //OBJECT[text()='toothbrush']]";

        // Create session
        try(BaseXClient session = new BaseXClient("128.105.144.71", 1984, "admin", "admin");
                BufferedWriter br = new BufferedWriter(new FileWriter(new File("data/output.txt")))) {

            // Open DB
            session.execute("open QIK");

            // Run query on database
            try(BaseXClient.Query query = session.query(lstQuery)) {
                // loop through all results
                while(query.more()) {
                    String output = query.next();
                    System.out.println(output);
                    br.write(output + "\n");
                    br.flush();
                }
                // print query info
                System.out.println(query.info());
            }

            // Drop database
            //session.execute("drop db QIK");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

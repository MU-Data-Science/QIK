package edu.umkc.Validate;

import edu.umkc.BaseX.BaseXClient;

import java.io.ByteArrayInputStream;
import java.io.InputStream;

public class BaseXValidator {

    public static void main(final String... args) {
        // Create session
        try(BaseXClient session = new BaseXClient("localhost", 1984, "admin", "admin")) {
            // Create empty database
            session.execute("create db QIK");

            // Open DB
            session.execute("open QIK");

            // To add a document
            // 1) A man and a dog are chasing a white cat.
            InputStream bais = new ByteArrayInputStream("<DOC><FILE>a.jpg</FILE><ROOT><S><NP><NP><DT>A</DT><NN>man</NN></NP><CC>and</CC><NP><DT>a</DT><NN>dog</NN></NP></NP><VP><VBP>are</VBP><VP><VBG>chasing</VBG><NP><DT>a</DT><JJ>white</JJ><NN>cat</NN></NP></VP></VP></S></ROOT></DOC>".getBytes());
            session.add("a.xml", bais);

            // 2) A man and a dog are chasing a black cat.
            bais = new ByteArrayInputStream("<DOC><FILE>b.jpg</FILE><ROOT><S><NP><NP><DT>A</DT><NN>man</NN></NP><CC>and</CC><NP><DT>a</DT><NN>dog</NN></NP></NP><VP><VBP>are</VBP><VP><VBG>chasing</VBG><NP><DT>a</DT><JJ>black</JJ><NN>cat</NN></NP></VP></VP></S></ROOT></DOC>".getBytes());
            session.add("a.xml", bais);

            //3) A man and a cat are chasing a white dog.
            bais = new ByteArrayInputStream("<DOC><FILE>c.jpg</FILE><ROOT><S><NP><NP><DT>A</DT><NN>man</NN></NP><CC>and</CC><NP><DT>a</DT><NN>cat</NN></NP></NP><VP><VBP>are</VBP><VP><VBG>chasing</VBG><NP><DT>a</DT><JJ>white</JJ><NN>dog</NN></NP></VP></VP></S></ROOT></DOC>".getBytes());
            session.add("a.xml", bais);

            // Run query on database
            //System.out.println(session.execute("find '//NN[text()=\"dog\"]'"));
            try(BaseXClient.Query query = session.query("//FILE[//NN[text()='dog']/following::VBG[text()='chasing']/following::NN[text()='cat']]/text()")) {
                // loop through all results
                while(query.more()) {
                    System.out.println(query.next());
                }
                // print query info
                System.out.println(query.info());
            }

            // Drop database
            session.execute("drop db QIK");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}

package edu.umkc.Constants;

public class Constants {

	public static final String PARSER_MODEL = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz";
	public static final String SOLR_URL = "http://localhost:8983/solr/QIK";
	public static final String NOUN_QUERY_STRING = "//NN | //NNS | //NNP | //NNPS";
	public static final String VERB_QUERY_STRING = "//VB  | //VBD | //VBG | //VBN | //VBP | //VBZ";
	public static final String NECC_DETAILS_QUERY_STRING = "//DT | //CC | //PRP | //IN | //WDT";
	public static final String UNIQUE_NECC_DETAILS_QUERY_STRING = "//*[substring(name(), 0,3) = \"DT\"] | //*[substring(name(), 0,3) = \"CC\"] | //*[substring(name(), 0,4) = \"PRP\"] | //*[substring(name(), 0,3) = \"IN\"] | //*[substring(name(), 0,4) = \"WDT\"]";
	public static final String FILE_QUERY_STRING = "//FILE/text()";
	public static final String ID_QUERY_STRING = "//FILE/@id";
	public static final String CAPTION_QUERY_STRING = "//CAPTION/text()";
	public static final String DEP_TREE_QUERY_STRING = "//DEP_TREE/text()";
	public static final String PARSE_TREE_QUERY_STRING = "//PARSE_TREE/text()";
	public static final Integer SOLR_FETCH_LIMIT=Integer.MAX_VALUE;
	public static final String DATA = "data";

	// BaseX
	public static final String DB_NAME = "QIK";
	public static final String BASEX_HOST = "localhost";
	public static final int BASEX_PORT = 1984;
	public static final String BASEX_USER = "admin";
	public static final String BASEX_PWD = "admin";

	// Lire
	public static final String IMAGE_DIR = "/mydata/apache-tomcat/webapps/QIK_Image_Data";
	public static final String INDEX_PATH= "index";
	public static final int LIRE_FETCH_LIMIT = 20;
	public static final String IMAGE_URL = "http://localhost:8080/QIK_Image_Data/";

	// Embeddings
	public static final int FILTER_SIZE = 10000;
	public static final String NOUN = "noun";
	public static final String VERB = "verb";
	public static final String EMBEDDING_URL = "http://localhost:5000/getNeighbours";
	public static final int EMBED_K = 3;
	public static final String EMBED_NOUN_QUERY_STRING = "//NN/text() | //NNS/text() | //NNP/text() | //NNPS/text()";
	public static final String EMBED_VERB_QUERY_STRING = "//VB/text()  | //VBD/text() | //VBG/text() | //VBN/text() | //VBP/text() | //VBZ/text()";

}

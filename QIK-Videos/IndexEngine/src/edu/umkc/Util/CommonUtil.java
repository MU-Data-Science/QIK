package edu.umkc.Util;

import com.google.gson.Gson;

import java.io.ByteArrayOutputStream;
import java.io.OutputStreamWriter;
import java.io.StringReader;
import java.io.StringWriter;
import java.util.*;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import com.google.gson.stream.JsonWriter;
import edu.umkc.Bean.QIKResultBean;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.w3c.dom.Document;
import org.xml.sax.InputSource;

public class CommonUtil {

	public static CommonUtil instance = null;
	private static final Logger logger = LogManager.getLogger(CommonUtil.class.getName());


	private CommonUtil() {

	}

	public static CommonUtil getInstance() {
		if (instance == null) {
			instance = new CommonUtil();
		}
		return instance;
	}

	public static Document convertStringToDocument(String xmlStr) {
		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
		DocumentBuilder builder;
		try {
			builder = factory.newDocumentBuilder();
			Document doc = builder.parse(new InputSource(new StringReader(xmlStr)));
			return doc;
		} catch (Exception e) {
			e.printStackTrace();
		}
		return null;
	}

	public static String convertDocumentToString(Document doc) {
		DOMSource domSource = new DOMSource(doc);
		StringWriter writer = new StringWriter();
		StreamResult result = new StreamResult(writer);
		TransformerFactory tf = TransformerFactory.newInstance();

		try {
			Transformer transformer = tf.newTransformer();
			transformer.transform(domSource, result);
			return writer.toString();
		} catch (Exception e) {
			e.printStackTrace();
		}
		return null;
	}

	public static String convertToJsonString(Map<Integer, List<QIKResultBean>> data) {
		Map<String, List<String>> map = new LinkedHashMap<String, List<String>>();
		Gson gson = new Gson();
		try {
			for(Integer idx: data.keySet()) {
				for (QIKResultBean bean : data.get(idx)) {
					String json = gson.toJson(bean, QIKResultBean.class);

					if (map.containsKey("\"" + idx+"\"")) {
						List<String> lst = map.get("\"" + idx+"\"");
						lst.add(json);
						map.put("\"" + idx+"\"", lst);
					} else {
						List<String> lst = new ArrayList<String>();
						lst.add(json);
						map.put("\"" + idx+"\"", lst);
					}
				}
			}

			return gson.toJson(map).replaceAll("\\\\\"", "'").replaceAll("\"", "").replaceAll("'", "\"");
		} catch (Exception e) {
			logger.error("CommonUtil :: convertToJsonString :: Exception encountered while conversion");
			e.printStackTrace();

		}

		return null;
	}
	
}

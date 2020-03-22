package edu.umkc.Util;

import java.util.ArrayList;
import java.util.List;

import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.apache.solr.common.SolrDocument;
import org.apache.solr.common.SolrDocumentList;
import org.apache.solr.common.SolrInputDocument;

import edu.umkc.Bean.SolrBean;
import edu.umkc.Constants.Constants;
import org.apache.solr.common.params.CommonParams;

public class SolrUtil {

	public static SolrUtil instance = null;
	public static SolrClient solrClient = null;

	private SolrUtil() {

	}

	public static SolrUtil getInstance() {
		if (instance == null) {
			try{
				solrClient = new HttpSolrClient.Builder(Constants.SOLR_URL).build();
			} catch (Exception e) {
				e.printStackTrace();
			}
			instance = new SolrUtil();
		}
		return instance;
	}

	public void uploadToSolr(SolrInputDocument doc) {
		try {
			System.out.println("SolrUtil :: uploadToSolr :: Adding the document.");
			solrClient.add(doc);

			System.out.println("SolrUtil :: uploadToSolr :: Commiting the transaction.");
			solrClient.commit();
			System.out.println("Document Uploaded to Solr Successfully");
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public List<SolrBean> querySolr(SolrQuery query) {
		try {
			QueryResponse response = solrClient.query(query);
			SolrDocumentList docList = response.getResults();

			if (docList != null && !docList.isEmpty()) {
				List<SolrBean> retList = new ArrayList<SolrBean>();
				for (SolrDocument doc : docList) {
					SolrBean solrBean = new SolrBean();
					solrBean.setKey(((List<String>) doc.getFieldValue("key")).get(0));
					solrBean.setCaption(((List<String>) doc.getFieldValue("caption")).get(0));
					solrBean.setVerbLst(((List<String>) doc.getFieldValue("verb")).get(0));
					solrBean.setNounLst(((List<String>) doc.getFieldValue("noun")).get(0));
					solrBean.setXml(((List<String>) doc.getFieldValue("tree")).get(0));
					retList.add(solrBean);
				}
				System.out.println("Queried Solr Successfully");
				return retList;
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
		return null;
	}

	public List<SolrBean> querySolr(String q) {
		try {
			SolrQuery query = new SolrQuery();
			query.set(CommonParams.Q, "*:*");
			query.setRows(Constants.SOLR_FETCH_LIMIT);
			return SolrUtil.getInstance().querySolr(query);
		} catch (Exception e) {
			e.printStackTrace();
		}
		return null;
	}

	public static List<SolrBean> queryMetaData(List<String> lst) {
		for(String id : lst) {
			SolrUtil.getInstance().querySolr("key: \"" + id + "\"");
			//Add to the list
		}

		return null;
	}
}

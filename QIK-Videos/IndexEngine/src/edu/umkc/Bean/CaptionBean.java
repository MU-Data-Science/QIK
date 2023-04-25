package edu.umkc.Bean;

public class CaptionBean {

	private String key;
	private String sceneId;
	private String[] captionsArr;
	private String[] depTreesArr;

	public String getKey() {
		return key;
	}

	public void setKey(String key) {
		this.key = key;
	}

	public String getSceneId() {
		return sceneId;
	}

	public void setSceneId(String sceneId) {
		this.sceneId = sceneId;
	}

	public String[] getCaptionsArr() {
		return captionsArr;
	}

	public void setCaptionsArr(String[] captionsArr) {
		this.captionsArr = captionsArr;
	}

	public String[] getDepTreesArr() {
		return depTreesArr;
	}

	public void setDepTreesArr(String[] depTreesArr) {
		this.depTreesArr = depTreesArr;
	}
}

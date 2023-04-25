package edu.umkc.Bean;

public class QIKResultBean {

    private String fileURL;
    private String sceneId;
    private String caption;
    private String depTree;
    private String parseTree;

    public String getFileURL() {
        return fileURL;
    }

    public String getSceneId() {
        return sceneId;
    }

    public String getCaption() {
        return caption;
    }

    public String getDepTree() { return depTree; }

    public String getParseTree() { return depTree; }

    public void setFileURL(String fileURL) {
        this.fileURL = fileURL;
    }

    public void setSceneId(String sceneId) {
        this.sceneId = sceneId;
    }

    public void setCaption(String caption) {
        this.caption = caption;
    }

    public void setDepTree(String depTree) { this.depTree = depTree; }

    public void setParseTree(String parseTree) { this.parseTree = parseTree; }

}

package edu.umkc.Bean;

public class QIKResultBean {

    private String fileURL;
    private String caption;
    private String depTree;
    private String parseTree;

    public String getFileURL() {
        return fileURL;
    }

    public void setFileURL(String fileURL) {
        this.fileURL = fileURL;
    }

    public String getCaption() {
        return caption;
    }

    public void setCaption(String caption) {
        this.caption = caption;
    }

    public String getDepTree() {
        return depTree;
    }

    public void setDepTree(String depTree) {
        this.depTree = depTree;
    }

    public String getParseTree() {
        return parseTree;
    }

    public void setParseTree(String parseTree) {
        this.parseTree = parseTree;
    }
}

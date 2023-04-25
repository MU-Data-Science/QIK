package edu.umkc.Validate;

import edu.umkc.BaseX.QueryMetaData;
import edu.umkc.BaseX.UploadMetaData;

public class UploadDataValidator {
    public static void main(String[] args) {
        QueryMetaData.getInstance().queryData("a group of chefs preparing food inside of a kitchen");
    }
}

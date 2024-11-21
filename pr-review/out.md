
### Review of Git Pull Request: UC-71165 show relationship in new UI

#### General Observations
1. **Title and Description**: The title and description provide a basic understanding of the changes. However, the description could be more detailed, especially regarding the technical changes and their impact.
2. **Code Quality**: The code generally follows good practices, but there are areas for improvement in terms of readability, maintainability, and adherence to best practices.

#### Specific Suggestions for Improvement

1. **Class `DrawingDTOBean`**:
    - **Serializable Implementation**: The class implements `Serializable`, which is good for potential serialization needs. However, it is important to ensure that all fields are serializable.
    - **Equals and HashCode**: The `equals` and `hashCode` methods are overridden, which is good practice. However, consider using `Objects.equals` for better readability and null safety.

    **Current Code**:
    ```java
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        DrawingDTOBean that = (DrawingDTOBean) o;
        return fileId == that.fileId && fileVersionId == that.fileVersionId;
    }

    @Override
    public int hashCode() {
        return Objects.hash(fileId, fileVersionId);
    }
    ```

    **Suggested Improvement**:
    ```java
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        DrawingDTOBean that = (DrawingDTOBean) o;
        return fileId == that.fileId && fileVersionId == that.fileVersionId;
    }

    @Override
    public int hashCode() {
        return Objects.hash(fileId, fileVersionId);
    }
    ```

2. **Class `DrawingTranslationRelationshipBean`**:
    - **Constructor Overloading**: The class has two constructors, which is good for flexibility. Ensure that the default constructor is necessary and used appropriately.
    - **Field Initialization**: Consider initializing fields directly if they have default values.

3. **Interface `RPCService` and `RPCServiceAsync`**:
    - **Method Naming**: The method `getDrawingsTranslationsForItem` could be renamed to `getDrawingTranslationsForItem` for consistency and clarity.
    - **Documentation**: Add Javadoc comments to the new methods to explain their purpose and usage.

    **Current Code**:
    ```java
    @AccessValidator(type = PART_VERSION, paramType = INTEGER, paramName = "partVersionId")
    List<DrawingTranslationRelationshipBean> getDrawingsTranslationsForItem(Integer partVersionId);
    ```

    **Suggested Improvement**:
    ```java
    /**
     * Retrieves the drawing translations for a given item version.
     *
     * @param partVersionId the ID of the part version
     * @return a list of drawing translation relationships
     */
    @AccessValidator(type = PART_VERSION, paramType = INTEGER, paramName = "partVersionId")
    List<DrawingTranslationRelationshipBean> getDrawingTranslationsForItem(Integer partVersionId);
    ```

4. **Class `UploadSystemTranslationsWindow`**:
    - **Error Handling**: The `onFailure` method in the `AsyncCallback` should log the error or provide user feedback.
    - **Code Duplication**: The code for setting attributes in the `onSuccess` method is duplicated. Consider refactoring into a separate method.

    **Current Code**:
    ```java
    @Override
    public void onFailure(Throwable caught) {
    }

    @Override
    public void onSuccess(List<DrawingTranslationRelationshipBean> drawingTranslations) {
        // Code for processing drawingTranslations
    }
    ```

    **Suggested Improvement**:
    ```java
    @Override
    public void onFailure(Throwable caught) {
        GWT.log("Failed to load drawing translations", caught);
    }

    @Override
    public void onSuccess(List<DrawingTranslationRelationshipBean> drawingTranslations) {
        processDrawingTranslations(drawingTranslations);
    }

    private void processDrawingTranslations(List<DrawingTranslationRelationshipBean> drawingTranslations) {
        java.util.Map<DrawingDTOBean, Record> recordMap = new java.util.HashMap<>();
        for (DrawingTranslationRelationshipBean dtbean : drawingTranslations) {
            DrawingDTOBean drawing = dtbean.getDrawing();
            TranslationsBean tbean = dtbean.getTranslation();
            Record record = recordMap.get(drawing);

            if (record == null) {
                record = new Record();
                record.setAttribute(DRAWING_VERSION, drawing.getFileVersion());
                record.setAttribute(DRAWING_NAME, sanitizeHtml(drawing.getFileName()));
                record.setAttribute(DRAWING_FILE_VERSION_ID, drawing.getFileVersionId());
                record.setAttribute(DRAWING_FILE_ID, drawing.getFileId());
                recordMap.put(drawing, record);
            }
            if (tbean != null) {
                String icon = "<img height='16px' width='16px' src='images/" + LoadImage.findImageByName(tbean.getFileName()) + "'></img>";
                setTranslationAttributes(record, tbean, icon);
            }
        }

        for (Record record : recordMap.values()) {
            list.addData(record);
        }
    }

    private void setTranslationAttributes(Record record, TranslationsBean tbean, String icon) {
        if (FileFormat.PDF.equalsIgnoreCase(tbean.getFileExtension())) {
            record.setAttribute(PDF_TRANSLATION_VERSION, tbean.getVersion());
            record.setAttribute(PDF_TRANSLATION, icon + sanitizeHtml(tbean.getFileName()));
            record.setAttribute(PDF_TRANSLATION_FILE_VERSION_ID, tbean.getPbFileVersionId());
            record.setAttribute(PDF_TRANSLATION_FILE_ID, tbean.getFileId());
        } else if (FileFormat.DWG.equalsIgnoreCase(tbean.getFileExtension())) {
            record.setAttribute(DWG_TRANSLATION_VERSION, tbean.getVersion());
            record.setAttribute(DWG_TRANSLATION, icon + sanitizeHtml(tbean.getFileName()));
            record.setAttribute(DWG_TRANSLATION_FILE_VERSION_ID, tbean.getPbFileVersionId());
            record.setAttribute(DWG_TRANSLATION_FILE_ID, tbean.getFileId());
        }
    }
    ```

5. **Class `TranslationsImplHelper`**:
    - **SQL Query**: The SQL query is embedded as a string, which can be error-prone and hard to maintain. Consider using a query builder or ORM for better readability and maintainability.
    - **Error Handling**: Ensure that all exceptions are logged with sufficient detail.

    **Current Code**:
    ```java
    String mssqlQuery = "SELECT DISTINCT top(100) ...";
    List<Object[]> result = userService.getSQLQueryResult(mssqlQuery);
    ```

    **Suggested Improvement**:
    ```java
    String mssqlQuery = buildDrawingTranslationQuery(partVersionId);
    List<Object[]> result = userService.getSQLQueryResult(mssqlQuery);

    private String buildDrawingTranslationQuery(Integer partVersionId) {
        return "SELECT DISTINCT top(100) ... WHERE pd.PB_PART_VERSION_ID = " + partVersionId + " ...";
    }
    ```

#### Conclusion
The PR introduces necessary changes to show relationships in the new UI. The suggestions provided aim to improve code readability, maintainability, and adherence to best practices. Implementing these changes will result in cleaner and more robust code.

### Review and Suggestions for Improvement

#### 1. **Code Design and Structure**

**Issue**: The `DrawingDTOBean` class is becoming a bit cluttered with the addition of new fields and methods. This can be improved by using a builder pattern for better readability and maintainability.

**Suggestion**: Implement the builder pattern for `DrawingDTOBean`.

**Current Code**:
```java
public class DrawingDTOBean implements Serializable {
    private static final long serialVersionUID = 1L;

    private int fileId;
    private int fileVersionId;
    private String fileName;
    private String fileVersion;
    private String fileExtension;
    private String fileSource;

    // Getters and Setters
}
```

**Improved Code**:
```java
public class DrawingDTOBean implements Serializable {
    private static final long serialVersionUID = 1L;

    private final int fileId;
    private final int fileVersionId;
    private final String fileName;
    private final String fileVersion;
    private final String fileExtension;
    private final String fileSource;

    private DrawingDTOBean(Builder builder) {
        this.fileId = builder.fileId;
        this.fileVersionId = builder.fileVersionId;
        this.fileName = builder.fileName;
        this.fileVersion = builder.fileVersion;
        this.fileExtension = builder.fileExtension;
        this.fileSource = builder.fileSource;
    }

    public static class Builder {
        private int fileId;
        private int fileVersionId;
        private String fileName;
        private String fileVersion;
        private String fileExtension;
        private String fileSource;

        public Builder fileId(int fileId) {
            this.fileId = fileId;
            return this;
        }

        public Builder fileVersionId(int fileVersionId) {
            this.fileVersionId = fileVersionId;
            return this;
        }

        public Builder fileName(String fileName) {
            this.fileName = fileName;
            return this;
        }

        public Builder fileVersion(String fileVersion) {
            this.fileVersion = fileVersion;
            return this;
        }

        public Builder fileExtension(String fileExtension) {
            this.fileExtension = fileExtension;
            return this;
        }

        public Builder fileSource(String fileSource) {
            this.fileSource = fileSource;
            return this;
        }

        public DrawingDTOBean build() {
            return new DrawingDTOBean(this);
        }
    }

    // Getters
}
```

#### 2. **Refactoring**

**Issue**: The `loadGridData` method in `UploadSystemTranslationsWindow` is doing too much. It fetches data and processes it in the same method, which violates the Single Responsibility Principle.

**Suggestion**: Separate the data fetching and processing logic into different methods.

**Current Code**:
```java
private void loadGridData() {
    ClientDataUtil.rpcService.getDrawingsTranslationsForItem(this.partVersionId, new AsyncCallback<List<DrawingTranslationRelationshipBean>>() {
        @Override
        public void onFailure(Throwable caught) {
        }

        @Override
        public void onSuccess(List<DrawingTranslationRelationshipBean> drawingTranslations) {
            java.util.Map<DrawingDTOBean, Record> recordMap = new java.util.HashMap<>();
            for (DrawingTranslationRelationshipBean dtbean : drawingTranslations) {
                DrawingDTOBean drawing = dtbean.getDrawing();
                TranslationsBean tbean = dtbean.getTranslation();
                Record record = recordMap.get(drawing);

                if (record == null) {
                    record = new Record();
                    record.setAttribute(DRAWING_VERSION, drawing.getFileVersion());
                    record.setAttribute(DRAWING_NAME, sanitizeHtml(drawing.getFileName()));
                    record.setAttribute(DRAWING_FILE_VERSION_ID, drawing.getFileVersionId());
                    record.setAttribute(DRAWING_FILE_ID, drawing.getFileId());
                    recordMap.put(drawing, record);
                }
                if (tbean != null) {
                    String icon = "<img height='16px' width='16px' src='images/" + LoadImage.findImageByName(tbean.getFileName()) + "'></img>";

                    if (FileFormat.PDF.equalsIgnoreCase(tbean.getFileExtension())) {
                        record.setAttribute(PDF_TRANSLATION_VERSION, tbean.getVersion());
                        record.setAttribute(PDF_TRANSLATION, icon + sanitizeHtml(tbean.getFileName()));
                        record.setAttribute(PDF_TRANSLATION_FILE_VERSION_ID, tbean.getPbFileVersionId());
                        record.setAttribute(PDF_TRANSLATION_FILE_ID, tbean.getFileId());
                    } else if (FileFormat.DWG.equalsIgnoreCase(tbean.getFileExtension())) {
                        record.setAttribute(DWG_TRANSLATION_VERSION, tbean.getVersion());
                        record.setAttribute(DWG_TRANSLATION, icon + sanitizeHtml(tbean.getFileName()));
                        record.setAttribute(DWG_TRANSLATION_FILE_VERSION_ID, tbean.getPbFileVersionId());
                        record.setAttribute(DWG_TRANSLATION_FILE_ID, tbean.getFileId());
                    }
                }
            }

            for (Record record : recordMap.values()) {
                list.addData(record);
            }
        }
    });
}
```

**Improved Code**:
```java
private void loadGridData() {
    ClientDataUtil.rpcService.getDrawingsTranslationsForItem(this.partVersionId, new AsyncCallback<List<DrawingTranslationRelationshipBean>>() {
        @Override
        public void onFailure(Throwable caught) {
            // Handle failure
        }

        @Override
        public void onSuccess(List<DrawingTranslationRelationshipBean> drawingTranslations) {
            processDrawingTranslations(drawingTranslations);
        }
    });
}

private void processDrawingTranslations(List<DrawingTranslationRelationshipBean> drawingTranslations) {
    java.util.Map<DrawingDTOBean, Record> recordMap = new java.util.HashMap<>();
    for (DrawingTranslationRelationshipBean dtbean : drawingTranslations) {
        DrawingDTOBean drawing = dtbean.getDrawing();
        TranslationsBean tbean = dtbean.getTranslation();
        Record record = recordMap.get(drawing);

        if (record == null) {
            record = new Record();
            record.setAttribute(DRAWING_VERSION, drawing.getFileVersion());
            record.setAttribute(DRAWING_NAME, sanitizeHtml(drawing.getFileName()));
            record.setAttribute(DRAWING_FILE_VERSION_ID, drawing.getFileVersionId());
            record.setAttribute(DRAWING_FILE_ID, drawing.getFileId());
            recordMap.put(drawing, record);
        }
        if (tbean != null) {
            String icon = "<img height='16px' width='16px' src='images/" + LoadImage.findImageByName(tbean.getFileName()) + "'></img>";

            if (FileFormat.PDF.equalsIgnoreCase(tbean.getFileExtension())) {
                record.setAttribute(PDF_TRANSLATION_VERSION, tbean.getVersion());
                record.setAttribute(PDF_TRANSLATION, icon + sanitizeHtml(tbean.getFileName()));
                record.setAttribute(PDF_TRANSLATION_FILE_VERSION_ID, tbean.getPbFileVersionId());
                record.setAttribute(PDF_TRANSLATION_FILE_ID, tbean.getFileId());
            } else if (FileFormat.DWG.equalsIgnoreCase(tbean.getFileExtension())) {
                record.setAttribute(DWG_TRANSLATION_VERSION, tbean.getVersion());
                record.setAttribute(DWG_TRANSLATION, icon + sanitizeHtml(tbean.getFileName()));
                record.setAttribute(DWG_TRANSLATION_FILE_VERSION_ID, tbean.getPbFileVersionId());
                record.setAttribute(DWG_TRANSLATION_FILE_ID, tbean.getFileId());
            }
        }
    }

    for (Record record : recordMap.values()) {
        list.addData(record);
    }
}
```

#### 3. **Performance**

**Issue**: The SQL query in `getDrawingTranslationRelationshipsForItem` method fetches a large number of columns, some of which might not be necessary.

**Suggestion**: Only select the columns that are required for the functionality.

**Current Code**:
```java
String mssqlQuery = "SELECT DISTINCT top(100) alldrawingfv.pb_file_version_id, alldrawingfv.file_name, alldrawingfv.version, alldrawingfv.PB_FILE_ID, alldrawingfv.CAD_INFO, drawingf.FILE_EXTENSION, drawingf.IS_VIRTUAL_FILE, drawingf.IS_HOOPS_FILE, drawingf.SYSTEM_GENERATED, alldrawingfv.conversion_status FvConversionStatus, translationfv.PB_FILE_VERSION_ID as translationFvid,translationfv.FILE_NAME as translationFilename,translationfv.version as translationVersion,translationfv.PB_FILE_ID as translationFileId,translationfv.CAD_INFO as translationCadInfo,translationf.FILE_EXTENSION as translationExtension " +
    " FROM " + dbPrefix + "PB_PART_DOC pd  " +
    " INNER JOIN  " + dbPrefix + "PB_DOC_FILE df ON df.PB_DOC_VERSION_ID = pd.PB_DOC_VERSION_ID  " +
    " INNER JOIN  " + dbPrefix + "PB_FILE_VERSION drawingfv ON drawingfv.PB_FILE_VERSION_ID = df.PB_FILE_VERSION_ID  " +
    " INNER JOIN  " + dbPrefix + "PB_FILE drawingf ON drawingfv.PB_FILE_ID = drawingf.PB_FILE_ID  " +
    " INNER JOIN  " + dbPrefix + "PB_FILE_VERSION alldrawingfv ON alldrawingfv.PB_FILE_ID = drawingf.PB_FILE_ID  " +
    " LEFT JOIN  " + dbPrefix + "FILE_TRANSLATION ft on ft.ORIGINAL_FILE_VERSION_ID = alldrawingfv.PB_FILE_VERSION_ID " +
    " LEFT JOIN  " + dbPrefix + "PB_FILE_VERSION translationfv on ft.TRANSLATION_FILE_VERSION_ID = translationfv.PB_FILE_VERSION_ID " +
    " LEFT JOIN  " + dbPrefix + "PB_FILE translationf on translationf.PB_FILE_ID = translationfv.PB_FILE_ID"+
    " WHERE pd.PB_PART_VERSION_ID =  " + partVersionId +
    " AND drawingf.IS_DRAWING = 1 " +
    " AND drawingf.TRANSACTION_ID is null " +
    " AND drawingfv.TRANSACTION_ID is null " +
    " AND alldrawingfv.TRANSACTION_ID is null " +
    " AND ft.TRANSACTION_ID is null " +
    " AND translationfv.TRANSACTION_ID is null " +
    " order by alldrawingfv.version desc;";
```

**Improved Code**:
```java
String mssqlQuery = "SELECT DISTINCT top(100) alldrawingfv.pb_file_version_id, alldrawingfv.file_name, alldrawingfv.version, alldrawingfv.PB_FILE_ID, drawingf.FILE_EXTENSION, translationfv.PB_FILE_VERSION_ID as translationFvid, translationfv.FILE_NAME as translationFilename, translationfv.version as translationVersion, translationfv.PB_FILE_ID as translationFileId, translationf.FILE_EXTENSION as translationExtension " +
    " FROM " + dbPrefix + "PB_PART_DOC pd  " +
    " INNER JOIN  " + dbPrefix + "PB_DOC_FILE df ON df.PB_DOC_VERSION_ID = pd.PB_DOC_VERSION_ID  " +
    " INNER JOIN  " + dbPrefix + "PB_FILE_VERSION drawingfv ON drawingfv.PB_FILE_VERSION_ID = df.PB_FILE_VERSION_ID  " +
    " INNER JOIN  " + dbPrefix + "PB_FILE drawingf ON drawingfv.PB_FILE_ID = drawingf.PB_FILE_ID  " +
    " INNER JOIN  " + dbPrefix + "PB_FILE_VERSION alldrawingfv ON alldrawingfv.PB_FILE_ID = drawingf.PB_FILE_ID  " +
    " LEFT JOIN  " + dbPrefix + "FILE_TRANSLATION ft on ft.ORIGINAL_FILE_VERSION_ID = alldrawingfv.PB_FILE_VERSION_ID " +
    " LEFT JOIN  " + dbPrefix + "PB_FILE_VERSION translationfv on ft.TRANSLATION_FILE_VERSION_ID = translationfv.PB_FILE_VERSION_ID " +
    " LEFT JOIN  " + dbPrefix + "PB_FILE translationf on translationf.PB_FILE_ID = translationfv.PB_FILE_ID"+
    " WHERE pd.PB_PART_VERSION_ID =  " + partVersionId +
    " AND drawingf.IS

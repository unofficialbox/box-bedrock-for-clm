/**
 * Uploads an inbound email's attachment(s) directly into the matching Opportunity's
 * Box folder, using the Box for Salesforce managed package's service-account auth.
 *
 * The file bytes come straight from the inbound email (never persisted in Salesforce
 * as a ContentVersion) — the file is stored once, in Box, and surfaces on the
 * Opportunity through the managed package's Box widget (record -> folder mapping).
 *
 * Runs as a Queueable so the Box callouts happen in their own transaction, clear of
 * Salesforce's "no callout after DML" rule (the handler logs the email activity first).
 */
public with sharing class BoxEmailAttachmentUploader implements Queueable, Database.AllowsCallouts {

    private static final String UPLOAD_URL = 'https://upload.box.com/api/2.0/files/content';

    /** Serializable carrier for one attachment (base64 so the Queueable state is serializable). */
    public class Attachment {
        public String fileName;
        public String base64Body;
        public Attachment(String fileName, String base64Body) {
            this.fileName = fileName;
            this.base64Body = base64Body;
        }
    }

    private final Id recordId;
    private final List<Attachment> attachments;
    private final String knownFolderId;

    public BoxEmailAttachmentUploader(Id recordId, List<Attachment> attachments) {
        this(recordId, attachments, null);
    }

    public BoxEmailAttachmentUploader(Id recordId, List<Attachment> attachments, String knownFolderId) {
        this.recordId = recordId;
        this.attachments = attachments;
        this.knownFolderId = knownFolderId;
    }

    public void execute(QueueableContext context) {
        if (attachments == null || attachments.isEmpty()) {
            return;
        }
        box.Toolkit tk = new box.Toolkit();

        // Resolve the record's Box folder. getFolderIdByRecordId is a Salesforce query
        // (no callout, no DML), so if the mapping already exists we can upload immediately.
        String folderId = String.isNotBlank(knownFolderId) ? knownFolderId : tk.getFolderIdByRecordId(recordId);

        if (String.isBlank(folderId)) {
            // Creating the mapping is a callout + DML. Salesforce forbids a callout after DML,
            // so create + commit here, then chain a second job that does the upload-only callouts.
            String created = tk.createObjectFolderForRecordId(recordId);
            tk.commitChanges();
            if (String.isBlank(created)) {
                System.debug(LoggingLevel.ERROR,
                    'BoxEmailAttachmentUploader: could not create Box folder for ' + recordId + ' :: ' + tk.mostRecentError);
                return;
            }
            if (!Test.isRunningTest()) {
                System.enqueueJob(new BoxEmailAttachmentUploader(recordId, attachments, created));
            }
            return;
        }

        // Folder already mapped: no toolkit DML in this path, so callouts are allowed.
        for (Attachment att : attachments) {
            uploadOne(tk, folderId, att.fileName, EncodingUtil.base64Decode(att.base64Body));
        }
    }

    /** Upload a single file to a Box folder via the managed service-account auth. Returns the Box file id (or null). */
    public static String uploadOne(box.Toolkit tk, String folderId, String fileName, Blob fileBody) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint(UPLOAD_URL);
        req.setMethod('POST');
        String boundary = '----clmEmailIntakeBoundary' + String.valueOf(fileBody.size());
        req.setHeader('Content-Type', 'multipart/form-data; boundary=' + boundary);
        req.setHeader('Accept', 'application/json');
        req.setBodyAsBlob(buildMultipart(boundary, fileName, folderId, fileBody));

        HttpResponse res = tk.sendRequest(req);
        Integer status = res.getStatusCode();
        if (status == 200 || status == 201) {
            return parseUploadedFileId(res.getBody());
        }
        System.debug(LoggingLevel.ERROR,
            'BoxEmailAttachmentUploader upload failed (' + status + '): ' + res.getBody());
        return null;
    }

    private static String parseUploadedFileId(String body) {
        try {
            Map<String, Object> root = (Map<String, Object>) JSON.deserializeUntyped(body);
            List<Object> entries = (List<Object>) root.get('entries');
            if (entries != null && !entries.isEmpty()) {
                return (String) ((Map<String, Object>) entries[0]).get('id');
            }
        } catch (Exception e) {
            // fall through
        }
        return null;
    }

    /**
     * Build a multipart/form-data body (Blob) with an "attributes" JSON part and a binary "file"
     * part. Apex cannot concatenate a String with a binary Blob directly, so the segments are
     * spliced in base64 with 3-byte alignment (the standard Box-on-Salesforce technique).
     */
    @TestVisible
    private static Blob buildMultipart(String boundary, String fileName, String folderId, Blob fileBody) {
        String safeName = fileName == null ? 'attachment' : fileName.replace('"', '');
        String attributes = '{"name":"' + safeName + '","parent":{"id":"' + folderId + '"}}';

        // Footer carries no leading CRLF here; each branch below adds the CRLF (or LF)
        // while re-encoding, so the file body and closing boundary stay byte-exact.
        String footer = '--' + boundary + '--';
        String header =
            '--' + boundary + '\r\n' +
            'Content-Disposition: form-data; name="attributes"\r\n\r\n' +
            attributes + '\r\n' +
            '--' + boundary + '\r\n' +
            'Content-Disposition: form-data; name="file"; filename="' + safeName + '"\r\n' +
            'Content-Type: application/octet-stream\r\n\r\n';

        // Pad the header so its base64 has no '=' padding (aligns to a 3-byte boundary).
        String headerEncoded = EncodingUtil.base64Encode(Blob.valueOf(header));
        while (headerEncoded.endsWith('=')) {
            header += ' ';
            headerEncoded = EncodingUtil.base64Encode(Blob.valueOf(header));
        }

        String bodyEncoded = EncodingUtil.base64Encode(fileBody);
        String last4 = bodyEncoded.substring(bodyEncoded.length() - 4);
        Blob assembled;
        if (last4.endsWith('==')) {
            // final quantum encodes 1 byte: rewrite tail, then append CRLF + footer on a fresh quantum
            bodyEncoded = bodyEncoded.substring(0, bodyEncoded.length() - 4) + last4.substring(0, 2) + '0K';
            String footerEncoded = EncodingUtil.base64Encode(Blob.valueOf('\r\n' + footer));
            assembled = EncodingUtil.base64Decode(headerEncoded + bodyEncoded + footerEncoded);
        } else if (last4.endsWith('=')) {
            // final quantum encodes 2 bytes: rewrite tail, then append LF + footer
            bodyEncoded = bodyEncoded.substring(0, bodyEncoded.length() - 4) + last4.substring(0, 3) + 'N';
            String footerEncoded = EncodingUtil.base64Encode(Blob.valueOf('\n' + footer));
            assembled = EncodingUtil.base64Decode(headerEncoded + bodyEncoded + footerEncoded);
        } else {
            // body already aligns to a 3-byte boundary
            String footerEncoded = EncodingUtil.base64Encode(Blob.valueOf('\r\n' + footer));
            assembled = EncodingUtil.base64Decode(headerEncoded + bodyEncoded + footerEncoded);
        }
        return assembled;
    }
}

/**
 * How many documents of each type sit across the contracts the caller can see.
 *
 * The contracts list holds no document data -- documents live in Box, one folder per
 * contract -- so a portfolio breakdown cannot be derived in the browser without a token
 * and a listing per contract. That would be two requests per row, and every one of them
 * would be a chance for a counterparty's browser to hold a token for a folder the page
 * never shows.
 *
 * So the aggregation happens here instead: one request in, counts out, no file names, no
 * file IDs, and no Box token leaving Apex.
 *
 * `with sharing` is the whole security model. The folders read are the folders of
 * contracts the running user can already see, so a counterparty's mix is drawn from their
 * own contracts and an internal user's from the portfolio. Box has no idea who is asking;
 * Salesforce decides, before Box is called at all.
 */
@RestResource(urlMapping='/clm/document-mix/*')
global with sharing class ClmDocumentMix {

    /** Folders read in one request. A portfolio bigger than this needs a different design. */
    private static final Integer MAX_FOLDERS = 25;

    global class TypeCount {
        global String label;
        global Integer count;
    }

    @HttpGet
    global static void getMix() {
        RestResponse response = RestContext.response;
        response.addHeader('Content-Type', 'application/json');
        response.addHeader('Cache-Control', 'no-store');

        try {
            Map<String, Integer> counts = new Counter().tally(new Reader().folders());
            List<TypeCount> mix = new List<TypeCount>();
            for (String label : counts.keySet()) {
                TypeCount entry = new TypeCount();
                entry.label = label;
                entry.count = counts.get(label);
                mix.add(entry);
            }
            response.statusCode = 200;
            response.responseBody = Blob.valueOf(JSON.serialize(mix));
        } catch (Exception e) {
            System.debug(LoggingLevel.WARN, 'CLM document mix failed: ' + e.getMessage());
            response.statusCode = 200;
            // An empty mix, not a 500: the chart is an extra on a page that works without
            // it, and a failed decoration should not look like a failed page.
            response.responseBody = Blob.valueOf('[]');
        }
    }

    /**
     * The Box folders of contracts this user can read.
     *
     * `with sharing` deliberately, and inherited from the outer class: this is the only
     * thing standing between a counterparty and a count of somebody else's documents.
     */
    private class Reader {
        private List<String> folders() {
            List<String> ids = new List<String>();
            for (CLM_Contract__c contract : [
                SELECT Box_Workspace_Folder_ID__c
                FROM CLM_Contract__c
                WHERE Box_Workspace_Folder_ID__c != null
                LIMIT :MAX_FOLDERS
            ]) {
                ids.add(contract.Box_Workspace_Folder_ID__c);
            }
            return ids;
        }
    }

    private class Counter {
        private Map<String, Integer> tally(List<String> folderIds) {
            Map<String, Integer> counts = new Map<String, Integer>();
            if (folderIds.isEmpty()) {
                return counts;
            }
            String token = ClmBoxAuth.parentToken();
            if (String.isBlank(token)) {
                return counts;
            }
            for (String folderId : folderIds) {
                for (String label : typesIn(folderId, token)) {
                    counts.put(label, (counts.containsKey(label) ? counts.get(label) : 0) + 1);
                }
            }
            return counts;
        }

        private List<String> typesIn(String folderId, String token) {
            List<String> labels = new List<String>();
            try {
                HttpRequest req = new HttpRequest();
                // `metadata.enterprise.<key>` is the shorthand for the caller's own
                // enterprise, so no enterprise ID has to be configured here.
                req.setEndpoint('callout:CLM_Box/2.0/folders/' + EncodingUtil.urlEncode(folderId, 'UTF-8')
                    + '/items?limit=200&fields=id,type,'
                    + EncodingUtil.urlEncode('metadata.enterprise.clmDocument', 'UTF-8'));
                req.setMethod('GET');
                req.setHeader('Authorization', 'Bearer ' + token);
                req.setTimeout(20000);
                HttpResponse res = new Http().send(req);
                if (res.getStatusCode() != 200) {
                    return labels;
                }
                Map<String, Object> body =
                    (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
                for (Object item : (List<Object>) body.get('entries')) {
                    Map<String, Object> entry = (Map<String, Object>) item;
                    if (entry.get('type') != 'file') {
                        continue;
                    }
                    labels.add(documentType(entry));
                }
            } catch (Exception e) {
                // One unreadable folder costs its own documents, not the whole chart.
                System.debug(LoggingLevel.WARN, 'CLM document mix: folder ' + folderId
                    + ' unreadable: ' + e.getMessage());
            }
            return labels;
        }

        private String documentType(Map<String, Object> entry) {
            Object metadata = entry.get('metadata');
            if (metadata != null) {
                Object enterprise = ((Map<String, Object>) metadata).get('enterprise');
                if (enterprise != null) {
                    Object instance = ((Map<String, Object>) enterprise).get('clmDocument');
                    if (instance != null) {
                        Object value = ((Map<String, Object>) instance).get('documentType');
                        if (value != null && String.isNotBlank(String.valueOf(value))) {
                            return String.valueOf(value);
                        }
                    }
                }
            }
            // An untagged file is counted and named, not dropped: a breakdown that silently
            // omits documents understates the package it claims to describe.
            return 'Unclassified';
        }
    }
}

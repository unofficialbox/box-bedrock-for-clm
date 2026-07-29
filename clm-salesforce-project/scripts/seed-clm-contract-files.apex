/*
 * Seed each contract's Opportunity Box folder with the contract document.
 * Run AFTER seed-clm-salesforce-sample-data.apex (records + per-year Opportunities must exist).
 *   sf apex run --target-org <alias> --file clm-salesforce-project/scripts/seed-clm-contract-files.apex
 *
 * Each CLM_Contract__c links to its own Opportunity, and Opportunity is the Box-mapped object, so
 * the file is uploaded into the contract's Opportunity Box folder. For each contract, enqueues
 * BoxEmailAttachmentUploader (resolves/creates the Opportunity's Box folder via box.Toolkit, then
 * uploads the file — preflight + version-if-exists). Bytes come from packaged Static Resources.
 *
 * Prior years get their EXECUTED PDF; the current year gets the in-redline Word document.
 * Uploads run asynchronously in Queueables.
 */
Map<String, String> fileByContract = new Map<String, String>{
    'CLM-SAMPLE-NST-2024' => 'Clm_Sample_Msa_2024_Executed:northstar-msa-2024-executed.pdf',
    'CLM-SAMPLE-NST-2025' => 'Clm_Sample_Msa_2025_Executed:northstar-msa-2025-executed.pdf',
    'CLM-SAMPLE-NST-001'  => 'Clm_Sample_Msa_2026_Redline:northstar-msa-2026-redline.docx'
};

// Upload into the contract's Opportunity Box folder (Opportunity is the Box-mapped object).
Map<String, Id> oppIdByContract = new Map<String, Id>();
for (CLM_Contract__c c : [SELECT Contract_ID__c, Opportunity__c FROM CLM_Contract__c WHERE Contract_ID__c IN :fileByContract.keySet()]) {
    if (c.Opportunity__c != null) {
        oppIdByContract.put(c.Contract_ID__c, c.Opportunity__c);
    }
}

Set<String> resourceNames = new Set<String>();
for (String spec : fileByContract.values()) {
    resourceNames.add(spec.substringBefore(':'));
}
Map<String, Blob> bodyByResource = new Map<String, Blob>();
for (StaticResource sr : [SELECT Name, Body FROM StaticResource WHERE Name IN :resourceNames]) {
    bodyByResource.put(sr.Name, sr.Body);
}

Integer enqueued = 0;
for (String contractExternalId : fileByContract.keySet()) {
    Id oppId = oppIdByContract.get(contractExternalId);
    if (oppId == null) {
        System.debug(LoggingLevel.WARN, 'CONTRACT FILES: no Opportunity for ' + contractExternalId + ' (seed records first)');
        continue;
    }
    String spec = fileByContract.get(contractExternalId);
    String resourceName = spec.substringBefore(':');
    String fileName = spec.substringAfter(':');
    Blob body = bodyByResource.get(resourceName);
    if (body == null) {
        System.debug(LoggingLevel.WARN, 'CONTRACT FILES: no static resource ' + resourceName);
        continue;
    }
    List<BoxEmailAttachmentUploader.Attachment> attachments = new List<BoxEmailAttachmentUploader.Attachment>{
        new BoxEmailAttachmentUploader.Attachment(fileName, EncodingUtil.base64Encode(body))
    };
    System.enqueueJob(new BoxEmailAttachmentUploader(oppId, attachments));
    enqueued++;
}
System.debug(LoggingLevel.INFO, 'CONTRACT FILES: enqueued ' + enqueued + ' upload job(s)');

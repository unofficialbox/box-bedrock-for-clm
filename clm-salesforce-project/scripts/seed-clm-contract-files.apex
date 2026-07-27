/*
 * Seed each CLM_Contract__c record's Box folder with its contract document.
 * Run AFTER seed-clm-salesforce-sample-data.apex (records must already exist).
 *   sf apex run --target-org <alias> --file clm-salesforce-project/scripts/seed-clm-contract-files.apex
 *
 * For each contract, enqueues BoxEmailAttachmentUploader (which resolves or creates the record's
 * Box folder via box.Toolkit, then uploads the file straight into it — preflight + version-if-exists).
 * The bytes come from packaged Static Resources (Apex can't read local files).
 *
 * Prior years get their EXECUTED PDF; the current year gets the in-redline Word document.
 *
 * Requires CLM_Contract__c to be a Box-mapped object in the Box for Salesforce managed package
 * (so the record -> folder mapping can be created). Uploads run asynchronously in Queueables.
 */
Map<String, String> fileByContract = new Map<String, String>{
    'CLM-SAMPLE-NST-2024' => 'Clm_Sample_Msa_2024_Executed:northstar-msa-2024-executed.pdf',
    'CLM-SAMPLE-NST-2025' => 'Clm_Sample_Msa_2025_Executed:northstar-msa-2025-executed.pdf',
    'CLM-SAMPLE-NST-001'  => 'Clm_Sample_Msa_2026_Redline:northstar-msa-2026-redline.docx'
};

Map<String, Id> recordIdByContract = new Map<String, Id>();
for (CLM_Contract__c c : [SELECT Id, Contract_ID__c FROM CLM_Contract__c WHERE Contract_ID__c IN :fileByContract.keySet()]) {
    recordIdByContract.put(c.Contract_ID__c, c.Id);
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
    Id recordId = recordIdByContract.get(contractExternalId);
    if (recordId == null) {
        System.debug(LoggingLevel.WARN, 'CONTRACT FILES: no CLM_Contract__c for ' + contractExternalId + ' (seed records first)');
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
    System.enqueueJob(new BoxEmailAttachmentUploader(recordId, attachments));
    enqueued++;
}
System.debug(LoggingLevel.INFO, 'CONTRACT FILES: enqueued ' + enqueued + ' upload job(s)');

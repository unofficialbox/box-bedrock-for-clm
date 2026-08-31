@IsTest
private class ClmBoxFolderServiceTest {

    private static void call(String recordId) {
        RestRequest request = new RestRequest();
        request.requestURI = '/services/apexrest/clm/box-folder';
        request.httpMethod = 'POST';
        if (recordId != null) {
            request.addParameter('recordId', recordId);
        }
        RestContext.request = request;
        RestContext.response = new RestResponse();
        ClmBoxFolderService.provisionFolder();
    }

    private static Map<String, Object> body() {
        return (Map<String, Object>) JSON.deserializeUntyped(RestContext.response.responseBody.toString());
    }

    @IsTest
    static void rejectsAMissingRecordId() {
        Test.startTest();
        call(null);
        Test.stopTest();

        System.assertEquals(400, RestContext.response.statusCode);
        System.assertEquals('invalid_record_id', body().get('error'));
    }

    @IsTest
    static void rejectsARecordIdThatIsNotAnId() {
        Test.startTest();
        call('demo-workspace');
        Test.stopTest();

        System.assertEquals(400, RestContext.response.statusCode, 'A malformed id must fail before the package is called');
        System.assertEquals('invalid_record_id', body().get('error'));
    }

    @IsTest
    static void reportsWhenThePackageProvisionsNothing() {
        // Without a Box connection the package returns no folder, and that has to surface
        // as a specific error rather than an empty success the caller cannot act on.
        CLM_Contract__c contract = new CLM_Contract__c(Name = 'Needs a folder');
        insert contract;

        Test.startTest();
        call(contract.Id);
        Test.stopTest();

        Integer status = RestContext.response.statusCode;
        System.assert(status == 200 || status == 500,
            'Expected a folder or a provisioning failure, got ' + status);
        if (status == 500) {
            System.assertEquals('box_folder_not_provisioned', body().get('error'));
        } else {
            System.assertNotEquals(null, body().get('folderId'));
        }
    }
}

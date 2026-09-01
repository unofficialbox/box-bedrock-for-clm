@IsTest
private class ClmContractListTest {

    private static void seed() {
        insert new List<CLM_Contract__c>{
            new CLM_Contract__c(Name = 'Northstar MSA', Contract_ID__c = 'CLM-A',
                Counterparty__c = 'Northstar Health', Status__c = 'Legal Review', Risk_Level__c = 'Critical'),
            new CLM_Contract__c(Name = 'Calder Master Agreement', Contract_ID__c = 'CLM-B',
                Counterparty__c = 'Calder Financial Group', Status__c = 'Legal Review', Risk_Level__c = 'Critical'),
            new CLM_Contract__c(Name = 'Meridian Renewal', Contract_ID__c = 'CLM-C',
                Counterparty__c = 'Meridian Labs', Status__c = 'Executed', Risk_Level__c = 'Low')
        };
    }

    private static ClmContractList.Result run(String status, String counterparty) {
        ClmContractList.Request request = new ClmContractList.Request();
        request.inputStatus = status;
        request.inputCounterparty = counterparty;
        return ClmContractList.listContracts(new List<ClmContractList.Request>{ request })[0];
    }

    @IsTest
    static void listsEveryContractWhenNothingIsFiltered() {
        seed();

        Test.startTest();
        ClmContractList.Result result = run(null, null);
        Test.stopTest();

        System.assertEquals(3, result.outputCount);
        System.assert(result.outputSummary.contains('CLM-A'), result.outputSummary);
        System.assert(result.outputSummary.contains('Northstar Health'), result.outputSummary);
        System.assert(result.outputSummary.contains('Status: Legal Review'), result.outputSummary);
    }

    @IsTest
    static void filtersByStatus() {
        seed();

        Test.startTest();
        ClmContractList.Result result = run('Legal Review', null);
        Test.stopTest();

        System.assertEquals(2, result.outputCount);
        System.assert(!result.outputSummary.contains('CLM-C'), 'Executed is not in Legal Review');
    }

    @IsTest
    static void filtersByCounterparty() {
        seed();

        Test.startTest();
        ClmContractList.Result result = run(null, 'Calder');
        Test.stopTest();

        System.assertEquals(1, result.outputCount);
        System.assert(result.outputSummary.contains('CLM-B'), result.outputSummary);
    }

    @IsTest
    static void saysSoRatherThanReturningAnEmptyListing() {
        seed();

        Test.startTest();
        ClmContractList.Result result = run('Signature', null);
        Test.stopTest();

        System.assertEquals(0, result.outputCount);
        System.assert(result.outputSummary.contains('No CLM contracts matched'), result.outputSummary);
    }
}

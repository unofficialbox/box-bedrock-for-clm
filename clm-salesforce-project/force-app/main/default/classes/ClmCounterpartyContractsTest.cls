/**
 * What is proved here is the filter: that a session bounded to one counterparty cannot
 * reach another's contracts, whatever is asked for.
 *
 * What is not proved here is record visibility for a real portal user. A Customer Community
 * user reaches their own account's rows through a sharing set, which is org configuration
 * rather than something a test can create -- and granting the test user View All to work
 * around that would grant the exact permission this class exists to avoid. So the bound
 * account is pinned, and the sharing set is called out in HANDOFF as a deployment step.
 */
@IsTest
private class ClmCounterpartyContractsTest {

    @TestSetup
    static void makeData() {
        Account northstar = new Account(Name = 'Northstar Health');
        Account calder = new Account(Name = 'Calder Financial Group');
        insert new List<Account>{ northstar, calder };

        insert new List<CLM_Contract__c>{
            new CLM_Contract__c(Name = 'Northstar MSA 2024', Contract_ID__c = 'CLM-NST-2024',
                Counterparty_Account__c = northstar.Id, Status__c = 'Executed', Term_Months__c = 36),
            new CLM_Contract__c(Name = 'Northstar MSA 2026', Contract_ID__c = 'CLM-NST-2026',
                Counterparty_Account__c = northstar.Id, Status__c = 'Legal Review'),
            new CLM_Contract__c(Name = 'Calder Master Agreement', Contract_ID__c = 'CLM-CAL-2026',
                Counterparty_Account__c = calder.Id, Status__c = 'Legal Review')
        };
    }

    private static Id accountNamed(String name) {
        return [SELECT Id FROM Account WHERE Name = :name LIMIT 1].Id;
    }

    private static ClmCounterpartyContracts.Result asCounterparty(String accountName, String reference) {
        ClmCounterpartyContracts.accountOverride = accountNamed(accountName);
        ClmCounterpartyContracts.Request request = new ClmCounterpartyContracts.Request();
        request.inputContract = reference;
        return ClmCounterpartyContracts.get(new List<ClmCounterpartyContracts.Request>{ request })[0];
    }

    @IsTest
    static void returnsOnlyTheSignedInCounterpartysContracts() {
        Test.startTest();
        ClmCounterpartyContracts.Result result = asCounterparty('Northstar Health', null);
        Test.stopTest();

        System.assertEquals(2, result.outputCount, result.outputSummary);
        System.assert(result.outputSummary.contains('CLM-NST-2024'), result.outputSummary);
        System.assert(!result.outputSummary.contains('CLM-CAL-2026'),
            'A counterparty must never see another organisation: ' + result.outputSummary);
    }

    @IsTest
    static void refusesAContractBelongingToAnotherCounterparty() {
        // The case the reference input exists to fail. Naming Calder's contract from a
        // Northstar session must not return it, however it is asked for.
        Test.startTest();
        ClmCounterpartyContracts.Result result = asCounterparty('Northstar Health', 'CLM-CAL-2026');
        Test.stopTest();

        System.assertEquals(0, result.outputCount);
        System.assert(result.outputSummary.contains('not a contract belonging to'), result.outputSummary);
        System.assert(!result.outputSummary.contains('Calder Master Agreement'),
            'The refusal must not leak the contract name: ' + result.outputSummary);
    }

    @IsTest
    static void narrowsToOneOfTheirOwnWhenNamed() {
        Test.startTest();
        ClmCounterpartyContracts.Result result = asCounterparty('Northstar Health', 'CLM-NST-2026');
        Test.stopTest();

        System.assertEquals(1, result.outputCount);
        System.assert(result.outputSummary.contains('CLM-NST-2026'), result.outputSummary);
        System.assert(!result.outputSummary.contains('CLM-NST-2024'), result.outputSummary);
    }

    @IsTest
    static void aCallerWithNoCounterpartySeesNothing() {
        // Staff have no Contact, so there is no account to bound to. The answer must not
        // quietly default to everything.
        Test.startTest();
        ClmCounterpartyContracts.Request request = new ClmCounterpartyContracts.Request();
        ClmCounterpartyContracts.Result result =
            ClmCounterpartyContracts.get(new List<ClmCounterpartyContracts.Request>{ request })[0];
        Test.stopTest();

        System.assertEquals(0, result.outputCount);
        System.assert(result.outputSummary.contains('cannot tell which'), result.outputSummary);
    }
}

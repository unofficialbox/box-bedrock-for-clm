/**
 * The Box listing is not exercised here.
 *
 * It goes through `box.Toolkit`, which owns its own credentials and its own callout, so
 * `Test.setMock` cannot stand in for it and the managed package returns nothing in a test
 * context. What that leaves testable is the half this class actually owns: finding the
 * contract, resolving its folder, and -- the part worth guarding -- keeping "Box refused"
 * distinct from "the folder is empty".
 *
 * The listing itself was verified against the live org and live Box on 2026-09-01:
 * `CLM-SAMPLE-NST-2024` returned all nine documents with their Box file IDs, and
 * `box__BoxAIAskByItemId` answered from the insurance certificate with real figures.
 */
@IsTest
private class ClmContractPackageTest {

    private static CLM_Contract__c contract() {
        CLM_Contract__c record = new CLM_Contract__c(
            Name = 'Northstar Health System MSA Package',
            Contract_ID__c = 'CLM-2026-0017',
            Counterparty__c = 'Northstar Health System',
            Status__c = 'Legal Review',
            Box_Workspace_Folder_ID__c = '413766128496'
        );
        insert record;
        return record;
    }

    private static ClmContractPackage.Result run(String reference) {
        ClmContractPackage.Request request = new ClmContractPackage.Request();
        request.inputContract = reference;
        return ClmContractPackage.get(new List<ClmContractPackage.Request>{ request })[0];
    }

    @IsTest
    static void resolvesTheContractAndItsFolder() {
        CLM_Contract__c record = contract();

        Test.startTest();
        ClmContractPackage.Result result = run('CLM-2026-0017');
        Test.stopTest();

        System.assertEquals(record.Id, result.outputRecordId);
        System.assertEquals('413766128496', result.outputFolderId,
            'With no Box association record, the folder falls back to the contract field');
        System.assert(result.outputSummary.contains('Northstar Health System'), result.outputSummary);
        System.assert(result.outputSummary.contains('Legal Review'), result.outputSummary);
    }

    @IsTest
    static void findsAContractByNameWhenTheReferenceIsNotExact() {
        contract();

        Test.startTest();
        ClmContractPackage.Result result = run('Northstar');
        Test.stopTest();

        System.assert(result.outputSummary.contains('CLM-2026-0017'), result.outputSummary);
    }

    @IsTest
    static void returnsTheResolvedReferenceWhateverTheCallerTyped() {
        // Whatever downstream stays bounded to this contract -- asking Box AI about one of
        // its documents -- needs the reference the lookup settled on, not the one that was
        // typed. Without this the agent bound an empty variable and the ask failed with
        // REQUIRED_FIELD_MISSING on contractReference.
        CLM_Contract__c record = contract();

        Test.startTest();
        ClmContractPackage.Result byName = run('Northstar');
        ClmContractPackage.Result byId = run(record.Id);
        Test.stopTest();

        System.assertEquals('CLM-2026-0017', byName.outputContractReference);
        System.assertEquals('CLM-2026-0017', byId.outputContractReference);
    }

    @IsTest
    static void findsAContractByRecordId() {
        CLM_Contract__c record = contract();

        Test.startTest();
        ClmContractPackage.Result result = run(record.Id);
        Test.stopTest();

        System.assertEquals(record.Id, result.outputRecordId);
    }

    @IsTest
    static void reportsAnEmptyPackageAsEmpty() {
        // In a test context the Toolkit answers with a folder carrying no entries, which
        // is the empty-folder shape. The refusal branch beside it -- `status` populated,
        // or the call throwing -- cannot be produced from here, so it is asserted by
        // reading the code rather than by this test: the two must stay distinguishable,
        // because reporting a broken credential as "no documents" is the failure that
        // would go unnoticed.
        contract();

        Test.startTest();
        ClmContractPackage.Result result = run('CLM-2026-0017');
        Test.stopTest();

        System.assertEquals(false, result.outputFound, 'An empty folder has nothing to cite');
        System.assert(result.outputSummary.contains('empty'), result.outputSummary);
    }

    @IsTest
    static void saysSoWhenTheContractHasNoBoxFolder() {
        insert new CLM_Contract__c(Name = 'No folder yet', Contract_ID__c = 'CLM-NO-FOLDER');

        Test.startTest();
        ClmContractPackage.Result result = run('CLM-NO-FOLDER');
        Test.stopTest();

        System.assertEquals(false, result.outputFound);
        System.assert(result.outputSummary.contains('no Box folder'), result.outputSummary);
    }

    @IsTest
    static void saysSoWhenNoContractMatches() {
        Test.startTest();
        ClmContractPackage.Result result = run('CLM-DOES-NOT-EXIST');
        Test.stopTest();

        System.assertEquals(false, result.outputFound);
        System.assert(result.outputSummary.contains('could not find'), result.outputSummary);
    }

    @IsTest
    static void asksForAReferenceWhenGivenNothing() {
        Test.startTest();
        ClmContractPackage.Result result = run('');
        Test.stopTest();

        System.assertEquals(false, result.outputFound);
        System.assert(result.outputSummary.contains('which contract'), result.outputSummary);
    }

    @IsTest
    static void documentIdsAreEmptyRatherThanNullForAKnownContract() {
        // The distinction the ask action depends on: a contract it can resolve returns a
        // set (possibly empty), and one it cannot returns null. Null means "I could not
        // confirm what belongs to this contract", which must never be read as "nothing
        // belongs to it, so allow the file".
        contract();

        Test.startTest();
        Set<String> ids = ClmContractPackage.documentIdsFor('CLM-2026-0017');
        Test.stopTest();

        System.assertNotEquals(null, ids, 'A resolvable contract must not look unresolvable');
        System.assertEquals(0, ids.size(), 'The Toolkit returns no documents in a test context');
    }

    @IsTest
    static void documentIdsAreNullWhenTheContractCannotBeResolved() {
        Test.startTest();
        Set<String> missing = ClmContractPackage.documentIdsFor('CLM-DOES-NOT-EXIST');
        Set<String> blank = ClmContractPackage.documentIdsFor('');
        Test.stopTest();

        System.assertEquals(null, missing);
        System.assertEquals(null, blank);
    }

    @IsTest
    static void documentIdsAreNullWhenTheContractHasNoFolder() {
        insert new CLM_Contract__c(Name = 'No folder yet', Contract_ID__c = 'CLM-NO-FOLDER-2');

        Test.startTest();
        Set<String> ids = ClmContractPackage.documentIdsFor('CLM-NO-FOLDER-2');
        Test.stopTest();

        System.assertEquals(null, ids, 'No folder means nothing can be confirmed as in scope');
    }
}

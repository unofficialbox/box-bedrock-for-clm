/**
 * The agent's entry point into a contract: the record, the governed Box folder, and the
 * Box file id of every document in it.
 *
 * Without this the Contract Copilot has nothing to act on. Its instructions tell it to
 * cite Box files, but the Box AI action addresses a file by id, and nothing in the
 * conversation supplies one -- so the agent could only promise to "gather the details"
 * and then answer from nothing. This turns a contract reference a person typed into the
 * ids the next action needs.
 *
 * The folder comes from the Box for Salesforce association, read with SOQL rather than
 * through box.Toolkit. The Toolkit read is harmless, but the provisioning call beside it
 * commits DML, and Apex forbids a callout after DML -- reading `box__FRUP__c` directly
 * keeps this method callout-safe by construction and reads the same rows the Toolkit
 * would. A contract with no association is reported as such rather than provisioned:
 * creating Box folders is not something a conversation should do on its own.
 *
 * The listing itself does go through box.Toolkit. It already holds the org's Box
 * credentials, so this needs no token grant, no named credential and no HTTP of its own --
 * one less place for the Box auth story to drift out of step.
 */
public with sharing class ClmContractPackage {

    public class Request {
        @InvocableVariable(
            label='Contract reference or record ID'
            description='A CLM contract reference such as CLM-2026-0017, the contract name, or a CLM_Contract__c record ID.'
            required=true
        )
        public String inputContract;
    }

    public class Result {
        @InvocableVariable(label='Contract package summary')
        public String outputSummary;
        @InvocableVariable(label='Salesforce record ID')
        public String outputRecordId;
        @InvocableVariable(label='Box folder ID')
        public String outputFolderId;
        @InvocableVariable(label='Whether a contract and its documents were found')
        public Boolean outputFound;
    }

    @InvocableMethod(
        label='Get CLM contract package'
        description='Finds a CLM contract, its governed Box folder, and every document in that folder with its Box file ID.'
    )
    public static List<Result> get(List<Request> requests) {
        List<Result> results = new List<Result>();
        for (Request req : requests) {
            results.add(build(req == null ? null : req.inputContract));
        }
        return results;
    }

    private static Result build(String reference) {
        Result result = new Result();
        result.outputFound = false;

        if (String.isBlank(reference)) {
            result.outputSummary = 'Tell me which contract you mean -- its reference, for example CLM-2026-0017.';
            return result;
        }

        CLM_Contract__c contract = new ContractLookup().byReference(reference.trim());
        if (contract == null) {
            result.outputSummary = 'I could not find a CLM contract matching "' + reference.trim() + '".';
            return result;
        }

        result.outputRecordId = contract.Id;
        String folderId = new FolderMapping().forRecord(contract.Id);
        if (String.isBlank(folderId)) {
            folderId = contract.Box_Workspace_Folder_ID__c;
        }
        result.outputFolderId = folderId;

        List<String> lines = new List<String>{ describe(contract) };

        if (String.isBlank(folderId)) {
            lines.add('This contract has no Box folder associated yet, so there are no documents to cite.');
            result.outputSummary = String.join(lines, '\n');
            return result;
        }

        List<String> files = listFiles(folderId);
        if (files == null) {
            lines.add('Box did not return the contents of folder ' + folderId + '. Do not guess at the documents.');
            result.outputSummary = String.join(lines, '\n');
            return result;
        }
        if (files.isEmpty()) {
            lines.add('The Box folder ' + folderId + ' is empty, so there is nothing to cite yet.');
            result.outputSummary = String.join(lines, '\n');
            return result;
        }

        lines.add('Documents in Box folder ' + folderId + ', with the file ID to ask Box AI about:');
        lines.addAll(files);
        result.outputFound = true;
        result.outputSummary = String.join(lines, '\n');
        return result;
    }

    private static String describe(CLM_Contract__c contract) {
        List<String> parts = new List<String>{ 'Contract ' + contract.Contract_ID__c + ' -- ' + contract.Name };
        if (String.isNotBlank(contract.Counterparty__c)) parts.add('Counterparty: ' + contract.Counterparty__c);
        if (String.isNotBlank(contract.Status__c)) parts.add('Status: ' + contract.Status__c);
        if (String.isNotBlank(contract.Risk_Level__c)) parts.add('Risk: ' + contract.Risk_Level__c);
        parts.add('Salesforce record: ' + contract.Id);
        return String.join(parts, '. ') + '.';
    }

    /**
     * The folder's files, one line each, or null when Box refused.
     *
     * Null and empty mean different things and the caller says so differently: an empty
     * folder is a real answer, a refusal is not, and collapsing them would let the agent
     * report "no documents" for what is actually a broken credential. box.Folder signals
     * a refusal by populating `status`, so an exception is not the only failure to catch.
     *
     * No commitChanges(): this reads and writes nothing, so there is no pending work.
     */
    private static List<String> listFiles(String folderId) {
        box.Folder contents;
        try {
            contents = new box.Toolkit().getFolderContents(folderId);
        } catch (Exception e) {
            System.debug(LoggingLevel.WARN, 'CLM Box: folder listing failed: ' + e.getMessage());
            return null;
        }
        if (contents == null || String.isNotBlank(contents.status)) {
            System.debug(LoggingLevel.WARN, 'CLM Box: folder listing refused: '
                + (contents == null ? 'no response' : contents.status));
            return null;
        }

        List<String> lines = new List<String>();
        if (contents.entries == null) {
            return lines;
        }
        for (box.Entry item : contents.entries) {
            if (item.type != 'file') {
                continue;
            }
            lines.add('- ' + item.name + ' (Box file ID ' + item.id + ')');
        }
        return lines;
    }

    /**
     * Finds the contract the way a person names one: by reference, by record id, or by
     * the contract's name. The reference is what appears in the workspace and in the
     * conversation, so it is tried first.
     */
    private with sharing class ContractLookup {
        private CLM_Contract__c byReference(String reference) {
            List<CLM_Contract__c> found = [
                SELECT Id, Name, Contract_ID__c, Counterparty__c, Status__c, Risk_Level__c,
                       Box_Workspace_Folder_ID__c
                FROM CLM_Contract__c
                WHERE Contract_ID__c = :reference
                LIMIT 1
            ];
            if (!found.isEmpty()) {
                return found[0];
            }
            if (reference instanceof Id) {
                found = [
                    SELECT Id, Name, Contract_ID__c, Counterparty__c, Status__c, Risk_Level__c,
                           Box_Workspace_Folder_ID__c
                    FROM CLM_Contract__c
                    WHERE Id = :reference
                    LIMIT 1
                ];
                if (!found.isEmpty()) {
                    return found[0];
                }
            }
            String pattern = '%' + reference + '%';
            found = [
                SELECT Id, Name, Contract_ID__c, Counterparty__c, Status__c, Risk_Level__c,
                       Box_Workspace_Folder_ID__c
                FROM CLM_Contract__c
                WHERE Name LIKE :pattern OR Contract_ID__c LIKE :pattern
                ORDER BY LastModifiedDate DESC
                LIMIT 1
            ];
            return found.isEmpty() ? null : found[0];
        }
    }

    /**
     * `without sharing` because the Box for Salesforce association records are not shared
     * with the agent user under normal sharing. It returns a folder id and grants no
     * record access; the contract itself is still read with sharing enforced above.
     */
    private without sharing class FolderMapping {
        private String forRecord(Id recordId) {
            List<box__FRUP__c> mappings = [
                SELECT box__Folder_ID__c
                FROM box__FRUP__c
                WHERE box__Record_ID__c = :String.valueOf(recordId)
                AND box__Folder_ID__c != null
                ORDER BY LastModifiedDate DESC
                LIMIT 1
            ];
            return mappings.isEmpty() ? null : mappings[0].box__Folder_ID__c;
        }
    }
}

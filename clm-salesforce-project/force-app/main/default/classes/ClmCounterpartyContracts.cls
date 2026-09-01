/**
 * What the person on the other side of the deal is allowed to see.
 *
 * The internal actions take a contract reference and trust the caller to name one they
 * should have. That is right for a contract manager working a portfolio, and wrong for a
 * counterparty: the Experience Cloud agent fills its arguments from the conversation, so
 * an action with a reference input is an action a counterparty can point at somebody
 * else's contract. Asking politely in the instructions is not a control.
 *
 * So this action has no reference input at all. It resolves the running user's Contact,
 * takes that Contact's Account, and returns only contracts whose Counterparty_Account__c
 * is that Account. There is nothing to abuse because there is nothing to supply.
 *
 * The Account lookup is the anchor rather than the Counterparty__c text, which carries
 * both "Northstar Health" and "Northstar Health System" for the same customer -- matching
 * on it would show a counterparty some of their contracts and hide the rest.
 *
 * An internal user has no Contact, and gets nothing. That is deliberate: this action
 * answers "what may this counterparty see", and for a member of staff the answer is not
 * "everything", it is "ask a different question".
 */
public with sharing class ClmCounterpartyContracts {

    private static final Integer MAX_RECORDS = 25;

    public class Request {
        @InvocableVariable(
            label='Contract reference'
            description='Optional. Narrow to one of the signed-in counterparty&apos;s own contracts. A reference belonging to anyone else is refused.'
        )
        public String inputContract;
    }

    public class Result {
        @InvocableVariable(label='Contracts this counterparty may see')
        public String outputSummary;
        @InvocableVariable(label='Counterparty account name')
        public String outputCounterparty;
        @InvocableVariable(label='How many contracts matched')
        public Integer outputCount;
    }

    @InvocableMethod(
        label='Get my counterparty contracts'
        description='Returns only the contracts belonging to the signed-in counterparty, resolved from their own account. Never returns another organisation&apos;s contracts, whatever is asked for.'
    )
    public static List<Result> get(List<Request> requests) {
        List<Result> results = new List<Result>();
        for (Request req : requests) {
            results.add(build(req == null ? null : req.inputContract));
        }
        return results;
    }

    /**
     * Lets a test pin the bound account.
     *
     * Record visibility for a portal user is a sharing question, not an Apex one -- a
     * community user reaches their own account's rows through a sharing set, which cannot
     * be conjured inside a test. Without this the filter could only be exercised by
     * granting the test user View All, and a test that grants the very permission the
     * class exists to avoid proves nothing.
     */
    @TestVisible
    private static Id accountOverride;

    /** The account this conversation is bounded to, exposed so a test can prove it. */
    @TestVisible
    private static Id boundAccount() {
        return accountOverride != null ? accountOverride : new IdentityResolver().accountForRunningUser();
    }

    private static Result build(String reference) {
        Result result = new Result();
        result.outputCount = 0;

        Id accountId = boundAccount();
        if (accountId == null) {
            result.outputSummary = 'I can only discuss contracts for the organisation you are signed in as, and I cannot tell which that is.';
            return result;
        }

        List<CLM_Contract__c> mine = new CounterpartyReader().read(accountId);
        if (mine.isEmpty()) {
            result.outputSummary = 'There are no contracts on file for your organisation.';
            return result;
        }
        result.outputCounterparty = mine[0].Counterparty_Account__r.Name;

        if (String.isNotBlank(reference)) {
            String wanted = reference.trim();
            for (CLM_Contract__c record : mine) {
                // String comparison on the id: `wanted == record.Id` coerces the left side
                // to an Id and throws on a reference like CLM-NST-2026.
                if (wanted.equalsIgnoreCase(record.Contract_ID__c)
                    || wanted.equalsIgnoreCase(String.valueOf(record.Id))) {
                    result.outputCount = 1;
                    result.outputSummary = describe(record);
                    return result;
                }
            }
            // Named, but not theirs. Say which organisation this conversation is bounded to
            // rather than implying the contract does not exist -- it does, just not here.
            result.outputSummary = wanted + ' is not a contract belonging to '
                + result.outputCounterparty + '. I can only discuss your own contracts.';
            return result;
        }

        List<String> lines = new List<String>{ 'Contracts for ' + result.outputCounterparty + ':' };
        for (CLM_Contract__c record : mine) {
            lines.add(describe(record));
        }
        result.outputCount = mine.size();
        result.outputSummary = String.join(lines, '\n');
        return result;
    }

    private static String describe(CLM_Contract__c record) {
        List<String> parts = new List<String>{ '- ' + record.Contract_ID__c + ' -- ' + record.Name };
        if (String.isNotBlank(record.Status__c)) parts.add('Status: ' + record.Status__c);
        if (record.Term_Months__c != null) parts.add('Term: ' + String.valueOf(record.Term_Months__c.intValue()) + ' months');
        return String.join(parts, ' | ');
    }

    /**
     * The running user's Account, by way of their Contact.
     *
     * `without sharing` only to read the caller's own User and Contact rows. It widens
     * nothing: the Account it returns is the caller's own, and it is the value everything
     * below is filtered by.
     */
    private without sharing class IdentityResolver {
        private Id accountForRunningUser() {
            // Schema-qualified: an unqualified User resolves ambiguously here and the
            // compiler reports it as "Illegal assignment from List<User> to List<User>".
            List<Schema.User> users = [
                SELECT ContactId, Contact.AccountId
                FROM User
                WHERE Id = :UserInfo.getUserId()
                LIMIT 1
            ];
            if (users.isEmpty() || users[0].ContactId == null) {
                return null;
            }
            return users[0].Contact.AccountId;
        }
    }

    /**
     * `without sharing` because CLM_Contract__c is Private/Private and a counterparty is
     * shared nothing. The account filter is the boundary, and it is applied here rather
     * than left to the caller -- which is the whole point of this class.
     */
    private without sharing class CounterpartyReader {
        private List<CLM_Contract__c> read(Id accountId) {
            return [
                SELECT Id, Name, Contract_ID__c, Status__c, Term_Months__c,
                       Counterparty_Account__r.Name
                FROM CLM_Contract__c
                WHERE Counterparty_Account__c = :accountId
                ORDER BY LastModifiedDate DESC
                LIMIT :MAX_RECORDS
            ];
        }
    }
}

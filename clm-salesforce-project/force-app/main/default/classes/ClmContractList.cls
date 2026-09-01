/**
 * The contracts in flight, so a question can be asked about a portfolio rather than one
 * named record.
 *
 * This exists because the alternative is worse. Without it, "where are we exposed across
 * open negotiations" can only be answered for contracts the person already knows to name,
 * which is exactly the blind spot the question is trying to close -- the exposure you have
 * not thought of is the one that hurts.
 *
 * It is deliberately not offered to the Experience Cloud agent. That surface serves a
 * counterparty looking at one contract, and enumerating the pipeline there would hand an
 * external party a list of every deal in the org. The same governed action, exposed on one
 * surface and withheld from the other, is the point rather than an oversight.
 *
 * The projection is fixed and narrow: enough to choose a contract to look at, and nothing
 * that would make this a data export. Amounts and counterparties are already visible to
 * anyone who can read the object.
 */
public with sharing class ClmContractList {

    /** Bounded so a portfolio question cannot turn into a table scan. */
    private static final Integer MAX_RECORDS = 50;

    public class Request {
        @InvocableVariable(
            label='Status filter'
            description='Optional. Return only contracts in this status: Intake, Legal Review, Business Review, Approved, Signature, Executed, or Obligations Active. Omit to return all, then filter from the statuses shown.'
        )
        public String inputStatus;
        @InvocableVariable(
            label='Counterparty filter'
            description='Optional. Return only contracts whose counterparty contains this text.'
        )
        public String inputCounterparty;
    }

    public class Result {
        @InvocableVariable(label='Contract list')
        public String outputSummary;
        @InvocableVariable(label='How many contracts matched')
        public Integer outputCount;
    }

    @InvocableMethod(
        label='List CLM contracts'
        description='Lists CLM contracts with their reference, counterparty, status, risk and value, so a portfolio question can be answered. Use the reference from here to get a contract package.'
    )
    public static List<Result> listContracts(List<Request> requests) {
        List<Result> results = new List<Result>();
        for (Request req : requests) {
            results.add(build(req));
        }
        return results;
    }

    private static Result build(Request req) {
        Result result = new Result();
        List<CLM_Contract__c> found = new ContractReader().read(
            req == null ? null : req.inputStatus,
            req == null ? null : req.inputCounterparty
        );
        result.outputCount = found.size();

        if (found.isEmpty()) {
            result.outputSummary = 'No CLM contracts matched.';
            return result;
        }

        List<String> lines = new List<String>{
            'CLM contracts (' + found.size() + (found.size() == MAX_RECORDS ? ', capped at ' + MAX_RECORDS : '') + '):'
        };
        for (CLM_Contract__c record : found) {
            List<String> parts = new List<String>{ '- ' + record.Contract_ID__c + ' -- ' + record.Name };
            if (String.isNotBlank(record.Counterparty__c)) parts.add(record.Counterparty__c);
            if (String.isNotBlank(record.Status__c)) parts.add('Status: ' + record.Status__c);
            if (String.isNotBlank(record.Risk_Level__c)) parts.add('Risk: ' + record.Risk_Level__c);
            if (record.Deal_Value__c != null) parts.add('Value: ' + record.Deal_Value__c.format());
            lines.add(String.join(parts, ' | '));
        }
        result.outputSummary = String.join(lines, '\n');
        return result;
    }

    /**
     * `without sharing` for the same reason as ClmContractListService: the agent user owns
     * no contracts and is shared none, so a record-scoped read returns an empty pipeline
     * and the answer reads as "you have no exposure" -- the most dangerous wrong answer
     * this action could give.
     */
    private without sharing class ContractReader {
        private List<CLM_Contract__c> read(String status, String counterparty) {
            String statusFilter = String.isBlank(status) ? null : status.trim();
            String counterpartyFilter = String.isBlank(counterparty) ? null : '%' + counterparty.trim() + '%';

            // Dynamic because both filters are optional and SOQL has no way to say
            // "ignore this predicate". The values stay bound rather than concatenated, so
            // a counterparty name carrying a quote is a search term and not an injection.
            List<String> predicates = new List<String>();
            if (statusFilter != null) {
                predicates.add('Status__c = :statusFilter');
            }
            if (counterpartyFilter != null) {
                predicates.add('Counterparty__c LIKE :counterpartyFilter');
            }
            String soql = 'SELECT Id, Name, Contract_ID__c, Counterparty__c, Status__c, '
                + 'Risk_Level__c, Deal_Value__c FROM CLM_Contract__c';
            if (!predicates.isEmpty()) {
                soql += ' WHERE ' + String.join(predicates, ' AND ');
            }
            soql += ' ORDER BY LastModifiedDate DESC LIMIT ' + MAX_RECORDS;
            return Database.query(soql);
        }
    }
}

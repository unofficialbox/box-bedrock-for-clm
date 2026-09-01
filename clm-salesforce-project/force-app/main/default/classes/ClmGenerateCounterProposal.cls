/**
 * Generates the counter-position memo for a contract on the counterparty's paper.
 *
 * On customer paper the useful artifact is not "the agreement" -- the agreement is theirs
 * and Acme is not going to redraft it. It is a position: the clause at issue, what their
 * draft says, the approved fallback and who owns the deviation, and what the counterparty
 * already agreed to. Box Doc Gen assembles those into one governed document that lands in
 * the contract's own folder.
 *
 * The split of authority matters and is deliberate. The **record** supplies the contract
 * facts -- id, counterparty, value, status -- so a caller cannot misattribute a memo to a
 * contract it is not about. The **caller** supplies the analysis, because the caller is
 * the agent that just read the clause library Hub and the prior executed agreements and
 * can cite both. The memo says so on its face: prepared as a draft, approval owned by a
 * named human.
 *
 * The Box credential stays in Apex. A client holding an MCP token holds no Box token.
 */
public with sharing class ClmGenerateCounterProposal {

    private static final String BATCH_ENDPOINT = 'callout:CLM_Box/2.0/docgen_batches';

    /**
     * Box Doc Gen is a versioned API and the version is not optional: without this header
     * the batch endpoint is not reachable at all, and with the wrong one Box answers 400
     * naming the versions it does accept.
     */
    private static final String DOCGEN_API_VERSION = '2025.0';

    public class Request {
        @InvocableVariable(
            label='Contract reference'
            description='The contract the memo is about, for example CLM-2026-0017. The contract facts on the memo come from that record, not from this request.'
            required=true
        )
        public String contractReference;
        @InvocableVariable(
            label='Clause at issue'
            description='Which clause of their paper is the problem, by number and name.'
            required=true
        )
        public String clauseAtIssue;
        @InvocableVariable(label='What their draft says')
        public String theirPosition;
        @InvocableVariable(label='Approved position' description='The approved clause and its ID from the clause library Hub.')
        public String approvedPosition;
        @InvocableVariable(label='Approved fallback' description='The approved fallback clause and its ID.')
        public String fallbackPosition;
        @InvocableVariable(label='Deviation owner' description='The named human who owns approval of this deviation.')
        public String owner;
        @InvocableVariable(label='What they agreed before' description='The precedent from prior executed agreements with this counterparty.')
        public String precedentSummary;
        @InvocableVariable(label='Proposed counter-position')
        public String counterProposal;
        @InvocableVariable(label='Their paper' description='The counterparty template this draft came in on, if known.')
        public String paperReference;
    }

    public class Result {
        @InvocableVariable(label='Outcome')
        public String summary;
        @InvocableVariable(label='Whether a document was generated')
        public Boolean generated;
        @InvocableVariable(label='Box Doc Gen batch ID')
        public String batchId;
    }

    @InvocableMethod(
        label='Generate a CLM counter-position memo'
        description='Generates the counter-position memo for a contract into its governed Box folder, from the approved clause library and prior executed agreements.'
    )
    public static List<Result> generate(List<Request> requests) {
        List<Result> results = new List<Result>();
        for (Request req : requests) {
            results.add(generateOne(req));
        }
        return results;
    }

    private static Result generateOne(Request req) {
        Result result = new Result();
        result.generated = false;

        if (req == null || String.isBlank(req.contractReference)) {
            result.summary = 'I need to know which contract the memo is for.';
            return result;
        }
        if (String.isBlank(req.clauseAtIssue)) {
            result.summary = 'I need the clause at issue before I can draft a position on it.';
            return result;
        }

        CLM_Box_Config__c config = CLM_Box_Config__c.getOrgDefaults();
        String templateId = config == null ? null : config.Counter_Position_Template_ID__c;
        if (String.isBlank(templateId)) {
            result.summary = 'No counter-position template is configured, so there is nothing to generate from.';
            return result;
        }

        ClmContractPackage.Located found = ClmContractPackage.locate(req.contractReference);
        if (found.contract == null) {
            result.summary = 'I could not find a CLM contract matching "'
                + req.contractReference.trim() + '".';
            return result;
        }
        if (String.isBlank(found.folderId)) {
            result.summary = 'Contract ' + found.contract.Contract_ID__c
                + ' has no Box folder, so there is nowhere governed to put the memo.';
            return result;
        }

        try {
            HttpRequest httpReq = new HttpRequest();
            httpReq.setEndpoint(BATCH_ENDPOINT);
            httpReq.setMethod('POST');
            httpReq.setHeader('Content-Type', 'application/json');
            httpReq.setHeader('box-version', DOCGEN_API_VERSION);
            httpReq.setHeader('Authorization', 'Bearer ' + ClmBoxAuth.parentToken());
            httpReq.setTimeout(60000);
            httpReq.setBody(JSON.serialize(body(req, found, templateId)));

            HttpResponse res = new Http().send(httpReq);
            // Doc Gen is asynchronous: 202 means the batch was accepted, not that the file
            // exists yet. Reporting it as done would be a lie by a few seconds, so the
            // summary says submitted and names where it will land.
            if (res.getStatusCode() == 202 || res.getStatusCode() == 201) {
                Map<String, Object> parsed =
                    (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
                result.batchId = String.valueOf(parsed.get('id'));
                result.generated = true;
                result.summary = 'Counter-position memo submitted for ' + found.contract.Contract_ID__c
                    + '. It lands in Box folder ' + found.folderId
                    + ' as ' + fileName(found.contract) + '.pdf. '
                    + 'It is a draft for review and does not approve anything.';
                return result;
            }
            result.summary = 'Box Doc Gen refused the request (' + res.getStatusCode()
                + '). No memo was generated.';
            System.debug(LoggingLevel.WARN, 'CLM DocGen: ' + res.getStatusCode() + ' ' + res.getBody());
        } catch (Exception e) {
            result.summary = 'The counter-position memo could not be generated.';
            System.debug(LoggingLevel.WARN, 'CLM DocGen failed: ' + e.getMessage());
        }
        return result;
    }

    /**
     * The Doc Gen payload.
     *
     * `user_input` keys are the template's tag namespace, not Salesforce field names --
     * the template is authored against this shape, so the two move together and a rename
     * on either side leaves an unresolved `{{tag}}` in the output rather than an error.
     */
    private static Map<String, Object> body(
        Request req,
        ClmContractPackage.Located found,
        String templateId
    ) {
        CLM_Contract__c contract = found.contract;
        Map<String, Object> userInput = new Map<String, Object>{
            'contract' => new Map<String, Object>{
                'id' => blankToDash(contract.Contract_ID__c),
                'counterparty' => blankToDash(contract.Counterparty__c),
                'paperReference' => blankToDash(req.paperReference),
                'dealValue' => contract.Deal_Value__c == null
                    ? '--' : String.valueOf(contract.Deal_Value__c),
                'status' => blankToDash(contract.Status__c)
            },
            'memo' => new Map<String, Object>{
                'preparedOn' => Datetime.now().format('d MMMM yyyy'),
                'preparedBy' => 'Contract Copilot (draft)'
            },
            'position' => new Map<String, Object>{
                'clauseAtIssue' => blankToDash(req.clauseAtIssue),
                'theirPosition' => blankToDash(req.theirPosition),
                'approvedPosition' => blankToDash(req.approvedPosition),
                'fallbackPosition' => blankToDash(req.fallbackPosition),
                'owner' => String.isBlank(req.owner) ? 'Commercial Legal' : req.owner.trim(),
                'risk' => blankToDash(contract.Risk_Level__c),
                'counterProposal' => blankToDash(req.counterProposal)
            },
            'precedent' => new Map<String, Object>{
                'summary' => String.isBlank(req.precedentSummary)
                    ? 'No prior executed agreement with this counterparty was cited.'
                    : req.precedentSummary.trim()
            }
        };

        return new Map<String, Object>{
            'file' => new Map<String, Object>{ 'id' => templateId, 'type' => 'file' },
            'input_source' => 'api',
            'destination_folder' => new Map<String, Object>{
                'id' => found.folderId, 'type' => 'folder'
            },
            'output_type' => 'pdf',
            'document_generation_data' => new List<Object>{
                new Map<String, Object>{
                    'generated_file_name' => fileName(contract),
                    'user_input' => userInput
                }
            }
        };
    }

    private static String fileName(CLM_Contract__c contract) {
        return 'counter-position-' + contract.Contract_ID__c;
    }

    /**
     * An em-dash rather than an empty string, because Doc Gen leaves an unfilled tag
     * looking like a rendering bug and a dash reads as "nothing to say here".
     */
    private static String blankToDash(String value) {
        return String.isBlank(value) ? '--' : value.trim();
    }
}

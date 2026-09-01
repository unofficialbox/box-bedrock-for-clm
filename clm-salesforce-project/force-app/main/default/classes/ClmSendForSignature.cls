/**
 * Prepares a Box Sign request for a contract document -- and stops short of sending it.
 *
 * The whole demo rests on the claim that autonomy stops at signature, so an action that
 * lets an agent put a contract in front of a signer would quietly falsify it. This one is
 * built so that it cannot:
 *
 *   - It refuses unless the contract has reached an approved state. A contract still in
 *     Legal Review is not signable and the refusal says which state it is in.
 *   - It bounds the document to the contract that was named, the same way reading one is
 *     bounded, so a Box file ID from somewhere else cannot be routed for signature.
 *   - It sets `is_document_preparation_needed`, which is the difference that matters.
 *     Box returns a prepare URL and sends nothing. A human opens that URL, places the
 *     fields, sees who it goes to, and presses send. The signature request exists; the
 *     decision to make it real stays with a person.
 *
 * So the honest description of this action is "get it ready for someone to send", and the
 * summary it returns says exactly that rather than implying a request went out.
 */
public with sharing class ClmSendForSignature {

    private static final String SIGN_ENDPOINT = 'callout:CLM_Box/2.0/sign_requests';

    /**
     * The contract states from which a signature request may be prepared. Anything earlier
     * is still being negotiated, and 'Executed' is already done.
     */
    private static final Set<String> SIGNABLE = new Set<String>{ 'Approved', 'Signature' };

    public class Request {
        @InvocableVariable(
            label='Contract reference'
            description='The contract being signed, for example CLM-2026-0017.'
            required=true
        )
        public String contractReference;
        @InvocableVariable(
            label='Box item ID'
            description='The Box file ID of the document to sign, taken from that contract\'s package listing.'
            required=true
        )
        public String itemId;
        @InvocableVariable(label='Signer email' required=true)
        public String signerEmail;
        @InvocableVariable(label='Signer name')
        public String signerName;
        @InvocableVariable(label='Email subject')
        public String subject;
    }

    public class Result {
        @InvocableVariable(label='Outcome')
        public String summary;
        @InvocableVariable(label='Whether a signature request was prepared')
        public Boolean prepared;
        @InvocableVariable(label='URL a human opens to review and send')
        public String prepareUrl;
        @InvocableVariable(label='Box Sign request ID')
        public String requestId;
    }

    @InvocableMethod(
        label='Prepare a Box Sign request for a CLM document'
        description='Prepares -- but does not send -- a Box Sign request for one contract document. Returns a URL a named human opens to review and send it.'
    )
    public static List<Result> prepare(List<Request> requests) {
        List<Result> results = new List<Result>();
        for (Request req : requests) {
            results.add(prepareOne(req));
        }
        return results;
    }

    private static Result prepareOne(Request req) {
        Result result = new Result();
        result.prepared = false;

        if (req == null || String.isBlank(req.contractReference)) {
            result.summary = 'I need to know which contract this document belongs to.';
            return result;
        }
        if (String.isBlank(req.itemId)) {
            result.summary = 'I need a Box file ID from the contract package before I can prepare a signature request.';
            return result;
        }
        if (String.isBlank(req.signerEmail)) {
            result.summary = 'I need a signer before I can prepare a signature request. I will not guess at one.';
            return result;
        }

        ClmContractPackage.Located found = ClmContractPackage.locate(req.contractReference);
        if (found.contract == null) {
            result.summary = 'I could not find a CLM contract matching "'
                + req.contractReference.trim() + '".';
            return result;
        }

        String status = found.contract.Status__c;
        if (!SIGNABLE.contains(status)) {
            result.summary = 'Contract ' + found.contract.Contract_ID__c + ' is ' + status
                + ', not approved for signature. Signature is blocked until the named approver'
                + ' completes their review; I cannot move it forward myself.';
            return result;
        }

        // The same bound reading a document has: the file must belong to this contract.
        Set<String> allowed = ClmContractPackage.documentIdsFor(req.contractReference);
        if (allowed == null) {
            result.summary = 'I could not resolve the documents for '
                + found.contract.Contract_ID__c + ', so I cannot confirm that file belongs to it.';
            return result;
        }
        if (!allowed.contains(req.itemId.trim())) {
            result.summary = 'That file is not in the Box folder for '
                + found.contract.Contract_ID__c + ', so it will not be sent for signature.';
            return result;
        }

        try {
            HttpRequest httpReq = new HttpRequest();
            httpReq.setEndpoint(SIGN_ENDPOINT);
            httpReq.setMethod('POST');
            httpReq.setHeader('Content-Type', 'application/json');
            httpReq.setHeader('Authorization', 'Bearer ' + ClmBoxAuth.parentToken());
            httpReq.setTimeout(60000);
            httpReq.setBody(JSON.serialize(body(req, found)));

            HttpResponse res = new Http().send(httpReq);
            if (res.getStatusCode() == 200 || res.getStatusCode() == 201) {
                Map<String, Object> parsed =
                    (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
                result.requestId = String.valueOf(parsed.get('id'));
                result.prepareUrl = parsed.get('prepare_url') == null
                    ? null : String.valueOf(parsed.get('prepare_url'));
                result.prepared = true;
                result.summary = 'A Box Sign request is prepared for '
                    + found.contract.Contract_ID__c + ' and addressed to '
                    + req.signerEmail.trim() + '. Nothing has been sent. Open the prepare URL'
                    + ' to place the signature fields and send it.';
                return result;
            }
            result.summary = 'Box Sign refused the request (' + res.getStatusCode()
                + '). Nothing was prepared and nothing was sent.';
            System.debug(LoggingLevel.WARN, 'CLM Sign: ' + res.getStatusCode() + ' ' + res.getBody());
        } catch (Exception e) {
            result.summary = 'The signature request could not be prepared. Nothing was sent.';
            System.debug(LoggingLevel.WARN, 'CLM Sign failed: ' + e.getMessage());
        }
        return result;
    }

    private static Map<String, Object> body(Request req, ClmContractPackage.Located found) {
        Map<String, Object> signer = new Map<String, Object>{
            'email' => req.signerEmail.trim(),
            'role' => 'signer'
        };
        if (String.isNotBlank(req.signerName)) {
            signer.put('name', req.signerName.trim());
        }
        return new Map<String, Object>{
            'source_files' => new List<Object>{
                new Map<String, Object>{ 'id' => req.itemId.trim(), 'type' => 'file' }
            },
            'parent_folder' => new Map<String, Object>{
                'id' => found.folderId, 'type' => 'folder'
            },
            'signers' => new List<Object>{ signer },
            'is_document_preparation_needed' => true,
            'subject' => String.isBlank(req.subject)
                ? 'Signature requested: ' + found.contract.Contract_ID__c
                : req.subject.trim()
        };
    }
}

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
 *
 * The callout goes through the Box managed package rather than straight to Box. That costs
 * a little directness and buys the thing a direct call cannot do: the package writes the
 * box__BoxSign__c record and stamps it with the record in `recordId`, so the signature
 * request appears on the contract it came from instead of existing only inside Box.
 */
public with sharing class ClmSendForSignature {

    /**
     * The contract states from which a signature request may be prepared. Anything earlier
     * is still being negotiated, and 'Executed' is already done.
     */
    private static final Set<String> SIGNABLE = new Set<String>{ 'Approved', 'Signature' };

    /** The configured fallback signer, or null where none is set. */
    private static String demoSigner() {
        CLM_Box_Config__c config = CLM_Box_Config__c.getOrgDefaults();
        return config == null ? null : config.Demo_Signer_Email__c;
    }

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
        @InvocableVariable(label='Signer email' description='Optional. Falls back to the configured demo signer; with neither, the request is refused rather than invented.')
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
        // A demo stalls on "who is signing?", and the honest answer in a demo is the person
        // running it -- not a guessed counterparty contact. Configuration supplies it, so no
        // address lives in source and a real environment that leaves it blank keeps the
        // refusal below.
        String signerEmail = String.isNotBlank(req.signerEmail) ? req.signerEmail : demoSigner();
        if (String.isBlank(signerEmail)) {
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
            SignOutcome outcome = sender.send(
                found.contract.Id, req.itemId.trim(), signerEmail.trim(),
                req.signerName, subjectFor(req, found));

            if (String.isBlank(outcome.requestId)) {
                result.summary = 'Box Sign refused the request. Nothing was prepared and'
                    + ' nothing was sent.';
                System.debug(LoggingLevel.WARN, 'CLM Sign: ' + outcome.error);
                return result;
            }

            result.requestId = outcome.requestId;
            result.prepareUrl = outcome.prepareUrl;
            result.prepared = true;
            result.summary = 'A Box Sign request is prepared for '
                + found.contract.Contract_ID__c + ' and addressed to '
                + signerEmail.trim() + '. Nothing has been sent. Open the prepare URL'
                + ' to place the signature fields and send it.';
            return result;
        } catch (Exception e) {
            result.summary = 'The signature request could not be prepared. Nothing was sent.';
            System.debug(LoggingLevel.WARN, 'CLM Sign failed: ' + e.getMessage());
        }
        return result;
    }

    private static String subjectFor(Request req, ClmContractPackage.Located found) {
        return String.isBlank(req.subject)
            ? 'Signature requested: ' + found.contract.Contract_ID__c
            : req.subject.trim();
    }

    /** What the Box Sign call gives back, in this class's own terms. */
    public class SignOutcome {
        public String requestId;
        public String prepareUrl;
        public Id recordId;
        public String error;
    }

    /**
     * The Box Sign call, behind a seam. The managed package's types cannot be mocked, so a
     * test stands in for the whole call rather than for an HTTP response.
     */
    public interface SignSender {
        SignOutcome send(Id contractId, String boxFileId, String signerEmail,
            String signerName, String subject);
    }

    @TestVisible
    private static SignSender sender = new PackageSender();

    private class PackageSender implements SignSender {
        public SignOutcome send(Id contractId, String boxFileId, String signerEmail,
            String signerName, String subject) {

            box.File file = new box.File();
            file.id = boxFileId;
            file.type = 'file';

            box.Signer signer = new box.Signer();
            signer.email = signerEmail;
            signer.role = 'signer';
            if (String.isNotBlank(signerName)) {
                signer.signer_name = signerName.trim();
            }

            box.BoxSignRequest request = new box.BoxSignRequest();
            // The record the signature request hangs off. The package resolves it to the
            // matching lookup on box__BoxSign__c, which is why that field has to point at
            // CLM_Contract__c and not at the standard Contract object.
            request.recordId = contractId;
            request.sf_files = new List<box.File>{ file };
            request.signers = new List<box.Signer>{ signer };
            request.subject = subject;
            request.is_document_preparation_needed = true;

            SignOutcome outcome = new SignOutcome();
            List<box.BoxSignResponse> responses =
                box.BoxSignService.sendSignRequests(new List<box.BoxSignRequest>{ request });
            if (responses == null || responses.isEmpty()) {
                outcome.error = 'Box Sign returned no response.';
                return outcome;
            }

            box.BoxSignResponse response = responses[0];
            outcome.requestId = response.id;
            outcome.prepareUrl = response.prepare_url;
            outcome.recordId = response.salesforce_id;
            outcome.error = response.error;
            return outcome;
        }
    }
}

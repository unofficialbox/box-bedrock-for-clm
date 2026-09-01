/**
 * Asks Box AI about one file, using the app's own credentials.
 *
 * The managed package ships `box__BoxAIAskByItemId`, and it is the obvious choice until
 * you run it as an agent: it authenticates as the *Salesforce user*, and an Agentforce
 * agent runs as its own user, which has never linked a Box account. The call comes back
 * 401 Unauthorized, and the conversation reports an authorization problem the person
 * cannot act on -- there is no Box login for them to fix.
 *
 * This takes the same route the rest of the workspace already takes: a Client Credentials
 * Grant for the configured Box subject, through the CLM_Box named credential. No per-user
 * Box linkage, and the same identity that lists the folder reads the file, so a document
 * the workspace can show is a document the agent can quote.
 */
public with sharing class ClmBoxAskDocument {

    private static final String ASK_ENDPOINT = 'callout:CLM_Box/2.0/ai/ask';

    public class Request {
        @InvocableVariable(
            label='Box item ID'
            description='The Box file ID to ask about, taken from the contract package listing, or a Box Hub ID.'
            required=true
        )
        public String itemId;
        @InvocableVariable(
            label='Box item type'
            description='"file" for one document, or "hub" to ask across a Box Hub such as the approved clause library. Defaults to file.'
        )
        public String itemType;
        @InvocableVariable(
            label='Prompt'
            description='The question to ask about that file.'
            required=true
        )
        public String prompt;
    }

    public class Result {
        @InvocableVariable(label='Answer')
        public String answer;
        @InvocableVariable(label='Whether Box AI answered')
        public Boolean answered;
    }

    @InvocableMethod(
        label='Ask Box AI about a CLM document'
        description='Asks Box AI a question about one contract document, identified by its Box file ID. The answer is grounded in that file.'
    )
    public static List<Result> ask(List<Request> requests) {
        List<Result> results = new List<Result>();
        for (Request req : requests) {
            results.add(askOne(req));
        }
        return results;
    }

    /**
     * The Box item type, defaulting to a single document.
     *
     * A Hub is how the approved clause library is asked about: one id standing for a
     * governed set of clauses, with Box AI citing the individual files it drew from.
     *
     * Box spells it `hubs`, plural, in `items[].type` -- the singular is rejected by the
     * enum with a 400, which is an easy hour to lose because the message names the schema
     * path rather than the accepted values. The singular is normalized here so a caller
     * who writes the obvious thing gets the working request.
     */
    private static String itemType(String requested) {
        String normalized = String.isBlank(requested) ? 'file' : requested.trim().toLowerCase();
        return normalized == 'hub' ? 'hubs' : normalized;
    }

    private static Result askOne(Request req) {
        Result result = new Result();
        result.answered = false;

        if (req == null || String.isBlank(req.itemId) || String.isBlank(req.prompt)) {
            result.answer = 'I need both a Box file ID and a question before I can read a document.';
            return result;
        }

        String token = ClmBoxAuth.parentToken();
        if (String.isBlank(token)) {
            result.answer = 'Box did not issue a token, so I could not read the document. This is a configuration problem, not something to retry.';
            return result;
        }

        Map<String, Object> item = new Map<String, Object>{
            'id' => req.itemId.trim(),
            'type' => itemType(req.itemType)
        };
        String body = JSON.serialize(new Map<String, Object>{
            'mode' => 'single_item_qa',
            'prompt' => req.prompt,
            'items' => new List<Object>{ item }
        });

        HttpRequest boxRequest = new HttpRequest();
        boxRequest.setEndpoint(ASK_ENDPOINT);
        boxRequest.setMethod('POST');
        boxRequest.setHeader('Authorization', 'Bearer ' + token);
        boxRequest.setHeader('Content-Type', 'application/json');
        // Box AI reads the document before answering, which is slower than a metadata call.
        boxRequest.setTimeout(120000);
        boxRequest.setBody(body);

        HttpResponse response;
        try {
            response = new Http().send(boxRequest);
        } catch (Exception e) {
            System.debug(LoggingLevel.WARN, 'CLM Box AI: request failed: ' + e.getMessage());
            result.answer = 'Box AI did not respond for that document.';
            return result;
        }

        if (response.getStatusCode() != 200 && response.getStatusCode() != 201) {
            System.debug(LoggingLevel.WARN, 'CLM Box AI: returned ' + response.getStatusCode() + ' ' + response.getBody());
            result.answer = 'Box AI refused to read that document (HTTP ' + response.getStatusCode() + '). Do not guess at its contents.';
            return result;
        }

        Map<String, Object> parsed = (Map<String, Object>) JSON.deserializeUntyped(response.getBody());
        String answer = (String) parsed.get('answer');
        if (String.isBlank(answer)) {
            result.answer = 'Box AI returned nothing for that document.';
            return result;
        }
        result.answer = answer;
        result.answered = true;
        return result;
    }
}

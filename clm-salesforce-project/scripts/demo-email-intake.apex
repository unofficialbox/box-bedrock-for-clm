/*
 * Demo: simulate a counterparty emailing a contract in.
 * Run with:  sf apex run --target-org <alias> --file clm-salesforce-project/scripts/demo-email-intake.apex
 *
 * Invokes EmailIntakeHandler exactly as the inbound Email Service would, using a
 * sample counterparty Contact address. It logs the email on the matching Opportunity
 * and uploads the attachment into that Opportunity's Box folder (stored once, in Box).
 *
 * Change SENDER to a Contact.Email that exists in the org, and SUBJECT/FILE_NAME as desired.
 */
String SENDER    = 'alex.mendoza@northstar.example';           // must match a Contact.Email
String SUBJECT   = 'Northstar MSA redline (demo)';
String FILE_NAME = 'northstar-msa-redline-demo.pdf';
Blob   FILE_BODY = Blob.valueOf('%PDF-1.7 demo contract payload — replace with a real PDF in a live send');

Messaging.InboundEmail email = new Messaging.InboundEmail();
email.fromAddress = SENDER;
email.fromName    = 'Counterparty Contact';
email.subject     = SUBJECT;
email.plainTextBody = 'Please find our redline attached for your review.';
email.toAddresses = new List<String>{ 'clm-intake@example.com' };
Messaging.InboundEmail.BinaryAttachment att = new Messaging.InboundEmail.BinaryAttachment();
att.fileName = FILE_NAME;
att.body     = FILE_BODY;
email.binaryAttachments = new List<Messaging.InboundEmail.BinaryAttachment>{ att };

Messaging.InboundEnvelope env = new Messaging.InboundEnvelope();
env.fromAddress = SENDER;

Messaging.InboundEmailResult res = new EmailIntakeHandler().handleInboundEmail(email, env);
System.debug('DEMO handler success=' + res.success);
System.debug('DEMO next: open the matched Opportunity — the email is on its timeline, ' +
    'and "' + FILE_NAME + '" is in the Opportunity Box folder (uploads asynchronously; give it a few seconds).');

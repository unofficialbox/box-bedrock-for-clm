@isTest
private class EmailIntakeHandlerTest {

    private static Messaging.InboundEmail buildEmail(String fromAddr, String subject, Boolean withAttachment) {
        Messaging.InboundEmail email = new Messaging.InboundEmail();
        email.fromAddress = fromAddr;
        email.fromName = 'Alex Mendoza';
        email.subject = subject;
        email.plainTextBody = 'Please find our redline attached.';
        email.toAddresses = new List<String>{ 'legal@acme.example' };
        if (withAttachment) {
            Messaging.InboundEmail.BinaryAttachment att = new Messaging.InboundEmail.BinaryAttachment();
            att.fileName = 'northstar-msa-redline-v3.pdf';
            att.body = Blob.valueOf('%PDF-1.7 fake bytes');
            email.binaryAttachments = new List<Messaging.InboundEmail.BinaryAttachment>{ att };
        }
        return email;
    }

    @isTest
    static void capturesEmailAndAttachmentOntoOpportunity() {
        Account acct = new Account(Name = 'Northstar Health', Website = 'https://www.northstar.example');
        insert acct;
        insert new Contact(
            FirstName = 'Alex', LastName = 'Mendoza',
            Email = 'alex.mendoza@northstar.example', AccountId = acct.Id
        );
        Opportunity opp = new Opportunity(
            Name = 'Northstar Master Service Agreement 2026',
            AccountId = acct.Id, StageName = 'Prospecting',
            CloseDate = Date.today().addMonths(3)
        );
        insert opp;

        Messaging.InboundEmail email = buildEmail('alex.mendoza@northstar.example', 'Northstar MSA redline v3', true);
        Messaging.InboundEnvelope env = new Messaging.InboundEnvelope();
        env.fromAddress = email.fromAddress;

        Test.startTest();
        Messaging.InboundEmailResult res = new EmailIntakeHandler().handleInboundEmail(email, env);
        Test.stopTest();

        System.assert(res.success, 'handler should report success');

        List<ContentDocumentLink> links = [
            SELECT Id FROM ContentDocumentLink WHERE LinkedEntityId = :opp.Id
        ];
        System.assertEquals(1, links.size(), 'attachment should be linked to the Opportunity');

        List<ContentVersion> cvs = [
            SELECT Id FROM ContentVersion WHERE Title = 'northstar-msa-redline-v3.pdf'
        ];
        System.assertEquals(1, cvs.size(), 'attachment should be saved as a File');

        Integer emails = [SELECT COUNT() FROM EmailMessage WHERE RelatedToId = :opp.Id];
        Integer tasks = [SELECT COUNT() FROM Task WHERE WhatId = :opp.Id];
        System.assert(emails + tasks >= 1, 'an email or task activity should be logged on the Opportunity');
    }

    @isTest
    static void matchesByDomainWhenNoContact() {
        Account acct = new Account(Name = 'Acme Cloudworks', Website = 'https://www.acmecloudworks.example');
        insert acct;
        Opportunity opp = new Opportunity(
            Name = 'Acme Cloudworks Cloud Security Expansion 2026',
            AccountId = acct.Id, StageName = 'Qualification',
            CloseDate = Date.today().addMonths(4)
        );
        insert opp;

        // No Contact for this sender; domain must match the Account website.
        Messaging.InboundEmail email = buildEmail('newperson@acmecloudworks.example', 'Expansion redline', true);
        Messaging.InboundEnvelope env = new Messaging.InboundEnvelope();

        Test.startTest();
        new EmailIntakeHandler().handleInboundEmail(email, env);
        Test.stopTest();

        List<ContentDocumentLink> links = [
            SELECT Id FROM ContentDocumentLink WHERE LinkedEntityId = :opp.Id
        ];
        System.assertEquals(1, links.size(), 'domain fallback should link the file to the Opportunity');
    }

    @isTest
    static void unmatchedSenderIsSafe() {
        Messaging.InboundEmail email = buildEmail('stranger@nowhere.example', 'hello', false);
        Messaging.InboundEnvelope env = new Messaging.InboundEnvelope();

        Test.startTest();
        Messaging.InboundEmailResult res = new EmailIntakeHandler().handleInboundEmail(email, env);
        Test.stopTest();

        System.assert(res.success, 'unmatched sender should still succeed (no bounce)');
        System.assertEquals(0, [SELECT COUNT() FROM ContentVersion], 'nothing captured for an unmatched sender');
    }
}

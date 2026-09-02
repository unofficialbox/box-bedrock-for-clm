// Seed sample Salesforce records for the CLM demo.
// Idempotent by keys:
// - Accounts by Name
// - Contacts by Email
// - Opportunities by Name + AccountId
// - Contracts by Contract_ID__c

Map<String, Account> accountsByName = new Map<String, Account>();
for (Account acct : [
    SELECT Id, Name
    FROM Account
    WHERE Name IN :new List<String>{
        'Northstar Health',
        'Halcyon Cloudworks'
    }
]) {
    accountsByName.put(acct.Name, acct);
}

Integer accountsCreated = 0;
List<Account> accountsToInsert = new List<Account>();
if (!accountsByName.containsKey('Northstar Health')) {
    accountsToInsert.add(new Account(
        Name = 'Northstar Health',
        Industry = 'Healthcare',
        Phone = '(212) 555-0101',
        Website = 'https://www.northstar.example'
    ));
}
if (!accountsByName.containsKey('Halcyon Cloudworks')) {
    accountsToInsert.add(new Account(
        Name = 'Halcyon Cloudworks',
        Industry = 'Technology',
        Phone = '(213) 555-0102',
        Website = 'https://www.acmecloudworks.example'
    ));
}
if (!accountsToInsert.isEmpty()) {
    insert accountsToInsert;
    accountsCreated += accountsToInsert.size();
}

accountsByName.clear();
for (Account acct : [
    SELECT Id, Name
    FROM Account
    WHERE Name IN :new List<String>{
        'Northstar Health',
        'Halcyon Cloudworks'
    }
]) {
    accountsByName.put(acct.Name, acct);
}

// ---------- Contacts ----------
Map<String, Contact> contactsByEmail = new Map<String, Contact>();
for (Contact c : [
    SELECT Id, Email
    FROM Contact
    WHERE Email IN :new List<String>{
        'alex.mendoza@northstar.example',
        'sarah.kim@acmecloudworks.example'
    }
]) {
    contactsByEmail.put(c.Email, c);
}

Integer contactsCreated = 0;
List<Contact> contactsToInsert = new List<Contact>();
if (!contactsByEmail.containsKey('alex.mendoza@northstar.example')) {
    contactsToInsert.add(new Contact(
        FirstName = 'Alex',
        LastName = 'Mendoza',
        Email = 'alex.mendoza@northstar.example',
        AccountId = accountsByName.get('Northstar Health').Id
    ));
}
if (!contactsByEmail.containsKey('sarah.kim@acmecloudworks.example')) {
    contactsToInsert.add(new Contact(
        FirstName = 'Sarah',
        LastName = 'Kim',
        Email = 'sarah.kim@acmecloudworks.example',
        AccountId = accountsByName.get('Halcyon Cloudworks').Id
    ));
}
if (!contactsToInsert.isEmpty()) {
    insert contactsToInsert;
    contactsCreated += contactsToInsert.size();
}

// ---------- Opportunities ----------
Map<String, Opportunity> opportunitiesByKey = new Map<String, Opportunity>();
for (Opportunity opp : [
    SELECT Id, Name, AccountId
    FROM Opportunity
    WHERE Name IN :new List<String>{
        'Northstar Master Service Agreement 2024',
        'Northstar Master Service Agreement 2025',
        'Northstar Master Service Agreement 2026',
        'Halcyon Cloudworks Cloud Security Expansion 2026'
    }
]) {
    opportunitiesByKey.put(opp.Name + '|' + opp.AccountId, opp);
}

Integer opportunitiesCreated = 0;
List<Opportunity> opportunitiesToInsert = new List<Opportunity>();

String northStarOppKey = 'Northstar Master Service Agreement 2026|' + accountsByName.get('Northstar Health').Id;
String northStar2024OppKey = 'Northstar Master Service Agreement 2024|' + accountsByName.get('Northstar Health').Id;
String northStar2025OppKey = 'Northstar Master Service Agreement 2025|' + accountsByName.get('Northstar Health').Id;
String acmeOppKey = 'Halcyon Cloudworks Cloud Security Expansion 2026|' + accountsByName.get('Halcyon Cloudworks').Id;

if (!opportunitiesByKey.containsKey(northStar2024OppKey)) {
    opportunitiesToInsert.add(new Opportunity(
        Name = 'Northstar Master Service Agreement 2024',
        AccountId = accountsByName.get('Northstar Health').Id,
        Amount = 2150000,
        CloseDate = Date.newInstance(2024, 7, 31),
        StageName = 'Closed Won'
    ));
}
if (!opportunitiesByKey.containsKey(northStar2025OppKey)) {
    opportunitiesToInsert.add(new Opportunity(
        Name = 'Northstar Master Service Agreement 2025',
        AccountId = accountsByName.get('Northstar Health').Id,
        Amount = 2275000,
        CloseDate = Date.newInstance(2025, 7, 31),
        StageName = 'Closed Won'
    ));
}
if (!opportunitiesByKey.containsKey(northStarOppKey)) {
    opportunitiesToInsert.add(new Opportunity(
        Name = 'Northstar Master Service Agreement 2026',
        AccountId = accountsByName.get('Northstar Health').Id,
        Amount = 250000,
        CloseDate = Date.today().addMonths(5),
        StageName = 'Prospecting'
    ));
}
if (!opportunitiesByKey.containsKey(acmeOppKey)) {
    opportunitiesToInsert.add(new Opportunity(
        Name = 'Halcyon Cloudworks Cloud Security Expansion 2026',
        AccountId = accountsByName.get('Halcyon Cloudworks').Id,
        Amount = 120000,
        CloseDate = Date.today().addMonths(6),
        StageName = 'Qualification'
    ));
}
if (!opportunitiesToInsert.isEmpty()) {
    insert opportunitiesToInsert;
    opportunitiesCreated += opportunitiesToInsert.size();
}

opportunitiesByKey.clear();
for (Opportunity opp : [
    SELECT Id, Name, AccountId
    FROM Opportunity
    WHERE Name IN :new List<String>{
        'Northstar Master Service Agreement 2024',
        'Northstar Master Service Agreement 2025',
        'Northstar Master Service Agreement 2026',
        'Halcyon Cloudworks Cloud Security Expansion 2026'
    }
]) {
    opportunitiesByKey.put(opp.Name + '|' + opp.AccountId, opp);
}

// ---------- Contracts ----------
Map<String, CLM_Contract__c> contractsByContractId = new Map<String, CLM_Contract__c>();
for (CLM_Contract__c contract : [
    SELECT Id, Contract_ID__c
    FROM CLM_Contract__c
    WHERE Contract_ID__c IN :new List<String>{
        'CLM-2026-0042',
        'CLM-2024-0311',
        'CLM-2025-0148',
        'CLM-2026-0088'
    }
]) {
    contractsByContractId.put(contract.Contract_ID__c, contract);
}

Integer contractsCreated = 0;
Integer contractsUpdated = 0;
List<CLM_Contract__c> contractsToInsert = new List<CLM_Contract__c>();
List<CLM_Contract__c> contractsToUpdate = new List<CLM_Contract__c>();

CLM_Contract__c northContract = contractsByContractId.get('CLM-2026-0042');
if (northContract == null) {
    northContract = new CLM_Contract__c(Contract_ID__c = 'CLM-2026-0042');
    contractsToInsert.add(northContract);
} else {
    contractsToUpdate.add(northContract);
}
northContract.Name = 'Northstar Health Master Service Agreement 2026';
northContract.Counterparty__c = 'Northstar Health';
northContract.Counterparty_Account__c = accountsByName.get('Northstar Health').Id;
northContract.Opportunity__c = opportunitiesByKey.get(northStarOppKey).Id;
northContract.Contract_Type__c = 'MSA Package';
northContract.Status__c = 'Legal Review';
northContract.Deal_Value__c = 250000;
northContract.Term_Months__c = 36;
northContract.Region__c = 'US';
northContract.Data_Category__c = 'None';
northContract.Target_Signature_Date__c = Date.today().addMonths(5);
northContract.Requester_Name__c = 'Alex Mendoza';
northContract.Requester_Email__c = 'alex.mendoza@northstar.example';
northContract.Business_Owner_Name__c = 'Northstar Master Contract Owner';
northContract.Record_Source__c = 'Manual';
northContract.Risk_Level__c = 'Medium';
northContract.Special_Terms_Risk_Notes__c = 'Sample contract record for demo use only.';

// Prior-year executed Northstar MSAs (contract history for the same customer).
CLM_Contract__c northContract2024 = contractsByContractId.get('CLM-2024-0311');
if (northContract2024 == null) {
    northContract2024 = new CLM_Contract__c(Contract_ID__c = 'CLM-2024-0311');
    contractsToInsert.add(northContract2024);
} else {
    contractsToUpdate.add(northContract2024);
}
northContract2024.Name = 'Northstar Health Master Service Agreement 2024';
northContract2024.Counterparty__c = 'Northstar Health';
northContract2024.Counterparty_Account__c = accountsByName.get('Northstar Health').Id;
northContract2024.Opportunity__c = opportunitiesByKey.get(northStar2024OppKey).Id;
northContract2024.Contract_Type__c = 'MSA Package';
northContract2024.Status__c = 'Executed';
northContract2024.Deal_Value__c = 2150000;
northContract2024.Term_Months__c = 36;
northContract2024.Region__c = 'US';
northContract2024.Data_Category__c = 'PHI';
northContract2024.Target_Signature_Date__c = Date.newInstance(2024, 7, 31);
northContract2024.Requester_Name__c = 'Alex Mendoza';
northContract2024.Requester_Email__c = 'alex.mendoza@northstar.example';
northContract2024.Business_Owner_Name__c = 'Northstar Master Contract Owner';
northContract2024.Record_Source__c = 'Manual';
northContract2024.Risk_Level__c = 'Low';
northContract2024.Special_Terms_Risk_Notes__c = 'Executed prior-year MSA; retained for demo contract history.';

CLM_Contract__c northContract2025 = contractsByContractId.get('CLM-2025-0148');
if (northContract2025 == null) {
    northContract2025 = new CLM_Contract__c(Contract_ID__c = 'CLM-2025-0148');
    contractsToInsert.add(northContract2025);
} else {
    contractsToUpdate.add(northContract2025);
}
northContract2025.Name = 'Northstar Health Master Service Agreement 2025';
northContract2025.Counterparty__c = 'Northstar Health';
northContract2025.Counterparty_Account__c = accountsByName.get('Northstar Health').Id;
northContract2025.Opportunity__c = opportunitiesByKey.get(northStar2025OppKey).Id;
northContract2025.Contract_Type__c = 'MSA Package';
northContract2025.Status__c = 'Executed';
northContract2025.Deal_Value__c = 2275000;
northContract2025.Term_Months__c = 36;
northContract2025.Region__c = 'US';
northContract2025.Data_Category__c = 'PHI';
northContract2025.Target_Signature_Date__c = Date.newInstance(2025, 7, 31);
northContract2025.Requester_Name__c = 'Alex Mendoza';
northContract2025.Requester_Email__c = 'alex.mendoza@northstar.example';
northContract2025.Business_Owner_Name__c = 'Northstar Master Contract Owner';
northContract2025.Record_Source__c = 'Manual';
northContract2025.Risk_Level__c = 'Low';
northContract2025.Special_Terms_Risk_Notes__c = 'Executed prior-year MSA; retained for demo contract history.';

CLM_Contract__c acmeContract = contractsByContractId.get('CLM-2026-0088');
if (acmeContract == null) {
    acmeContract = new CLM_Contract__c(Contract_ID__c = 'CLM-2026-0088');
    contractsToInsert.add(acmeContract);
} else {
    contractsToUpdate.add(acmeContract);
}
acmeContract.Name = 'Halcyon Cloudworks Cloud Security Expansion 2026';
acmeContract.Counterparty__c = 'Halcyon Cloudworks';
acmeContract.Counterparty_Account__c = accountsByName.get('Halcyon Cloudworks').Id;
acmeContract.Opportunity__c = opportunitiesByKey.get(acmeOppKey).Id;
acmeContract.Contract_Type__c = 'SOW';
acmeContract.Status__c = 'Intake';
acmeContract.Deal_Value__c = 120000;
acmeContract.Term_Months__c = 24;
acmeContract.Region__c = 'Global';
acmeContract.Data_Category__c = 'Confidential';
acmeContract.Target_Signature_Date__c = Date.today().addMonths(6);
acmeContract.Requester_Name__c = 'Sarah Kim';
acmeContract.Requester_Email__c = 'sarah.kim@acmecloudworks.example';
acmeContract.Business_Owner_Name__c = 'Halcyon Cloud Contract Owner';
acmeContract.Record_Source__c = 'Manual';
acmeContract.Risk_Level__c = 'Medium';
acmeContract.Special_Terms_Risk_Notes__c = 'Sample contract record for demo use only.';

if (!contractsToInsert.isEmpty()) {
    insert contractsToInsert;
    contractsCreated += contractsToInsert.size();
}
if (!contractsToUpdate.isEmpty()) {
    update contractsToUpdate;
    contractsUpdated += contractsToUpdate.size();
}

System.debug(LoggingLevel.INFO, 'SEED COMPLETE accounts new=' + accountsCreated + ' contacts new=' + contactsCreated + ' opportunities new=' + opportunitiesCreated + ' contracts new=' + contractsCreated + ' contracts updated=' + contractsUpdated);
System.debug(LoggingLevel.INFO, 'SEED IDS: ' +
    'account.Northstar=' + accountsByName.get('Northstar Health').Id +
    ', account.Acme=' + accountsByName.get('Halcyon Cloudworks').Id +
    ', opp.Northstar=' + opportunitiesByKey.get(northStarOppKey).Id +
    ', opp.Acme=' + opportunitiesByKey.get(acmeOppKey).Id +
    ', contract.NST=' + (northContract.Id == null ? 'pending_insert' : northContract.Id) +
    ', contract.ACM=' + (acmeContract.Id == null ? 'pending_insert' : acmeContract.Id));

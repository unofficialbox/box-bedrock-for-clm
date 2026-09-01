import { createDataSDK, gql } from "@salesforce/platform-sdk";
import type { ClmContractSummary } from "./contracts";

/**
 * Read contracts through the GraphQL UI API instead of custom Apex.
 *
 * This is the pattern the official React-on-Platform recipes use
 * (trailheadapps/multiframework-recipes). It runs as the logged-in user, so sharing and
 * field-level security are enforced by the platform rather than by a hand-written
 * projection -- which is why it is worth preferring over ClmContractListService once the
 * surface is authenticated.
 *
 * It returns nothing for the Experience Cloud guest user, which holds no records. That
 * is the whole point: the guest path needs a sharing rule that publishes contracts to
 * anonymous visitors, and this path does not.
 */
const GET_CLM_CONTRACTS = gql`
  query GetClmContracts {
    uiapi {
      query {
        CLM_Contract__c(first: 50, orderBy: { LastModifiedDate: { order: DESC } }) {
          edges {
            node {
              Id
              Name { value }
              Contract_ID__c { value }
              Counterparty__c { value }
              Contract_Type__c { value }
              Status__c { value }
              Risk_Level__c { value }
              Deal_Value__c { value }
              Term_Months__c { value }
              Box_Workspace_Folder_ID__c { value }
            }
          }
        }
      }
    }
  }
`;

interface FieldValue<T> {
  value: T | null;
}

interface ContractNode {
  Id: string;
  Name?: FieldValue<string>;
  Contract_ID__c?: FieldValue<string>;
  Counterparty__c?: FieldValue<string>;
  Contract_Type__c?: FieldValue<string>;
  Status__c?: FieldValue<string>;
  Risk_Level__c?: FieldValue<string>;
  Deal_Value__c?: FieldValue<number>;
  Term_Months__c?: FieldValue<number>;
  Box_Workspace_Folder_ID__c?: FieldValue<string>;
}

interface ContractsQuery {
  uiapi?: {
    query?: {
      CLM_Contract__c?: { edges?: ({ node?: ContractNode } | null)[] | null } | null;
    };
  };
}

/**
 * Null means "this path is not available here" -- the SDK is absent or the surface does
 * not provide it -- which the caller uses to fall back to Apex. An empty array means the
 * query ran and the user can see no contracts, which is a different answer and must not
 * trigger a fallback.
 */
export async function fetchContractsViaGraphql(): Promise<ClmContractSummary[] | null> {
  try {
    const sdk = await createDataSDK();
    if (!sdk?.graphql) {
      console.info("[CLM] Platform SDK has no GraphQL on this surface; using the Apex endpoint.");
      return null;
    }
    const result = await sdk.graphql.query<ContractsQuery>({ query: GET_CLM_CONTRACTS });
    const edges = result?.data?.uiapi?.query?.CLM_Contract__c?.edges;
    if (!edges) {
      console.info("[CLM] GraphQL returned no contract connection; using the Apex endpoint.");
      return null;
    }
    return edges.flatMap((edge) => {
      const node = edge?.node;
      if (!node) return [];
      return [{
        recordId: node.Id,
        name: node.Name?.value ?? undefined,
        contractId: node.Contract_ID__c?.value ?? undefined,
        counterparty: node.Counterparty__c?.value ?? undefined,
        contractType: node.Contract_Type__c?.value ?? undefined,
        status: node.Status__c?.value ?? undefined,
        riskLevel: node.Risk_Level__c?.value ?? undefined,
        dealValue: node.Deal_Value__c?.value ?? undefined,
        termMonths: node.Term_Months__c?.value ?? undefined,
        boxFolderId: node.Box_Workspace_Folder_ID__c?.value ?? undefined,
      }];
    });
  } catch (error) {
    console.info("[CLM] Platform SDK unavailable here; using the Apex endpoint.", error);
    return null;
  }
}

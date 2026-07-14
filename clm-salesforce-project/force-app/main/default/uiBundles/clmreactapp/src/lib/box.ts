import { CLM_CONFIG } from "../config";

declare global {
  interface Window {
    __CLM_RUNTIME_CONFIG__?: {
      boxAccessToken?: string;
      agentforceAgentId?: string;
      agentforceAppId?: string;
      salesforceOrigin?: string;
    };
    Box?: {
      ContentExplorer: new () => {
        show(folderId: string, accessToken: string, options: Record<string, unknown>): void;
        hide(): void;
        removeAllListeners(): void;
      };
    };
  }
}

export interface ClmPageContext {
  contractId: string;
  folderId: string;
  salesforceRecordId?: string;
}

export function getClmPageContext(search = window.location.search): ClmPageContext {
  const params = new URLSearchParams(search);
  const salesforceRecordId = params.get("recordId");
  return {
    contractId: params.get("contractId") || "CLM-2026-0017",
    folderId: params.get("folderId") || CLM_CONFIG.workspace.folderId,
    ...(salesforceRecordId ? { salesforceRecordId } : {}),
  };
}

export function getAgentContextPrompt(search = window.location.search): string {
  const { contractId, folderId, salesforceRecordId } = getClmPageContext(search);
  const context = [
    `Current CLM contract: ${contractId}.`,
    `Governed Box workspace folder ID: ${folderId}.`,
  ];
  if (salesforceRecordId) context.push(`Salesforce CLM record ID: ${salesforceRecordId}.`);
  context.push(
    "Use Box as the source of truth. Cite files for every material contract claim.",
    "Do not approve legal language, complete approval tasks, or send for signature without a named human decision."
  );
  return context.join("\n");
}

export async function fetchDownscopedBoxToken(folderId: string): Promise<string> {
  const injectedToken = window.__CLM_RUNTIME_CONFIG__?.boxAccessToken;
  if (injectedToken) return injectedToken;

  try {
    const response = await fetch(
      `/services/apexrest/clm/box-token?folderId=${encodeURIComponent(folderId)}`,
      { headers: { Accept: "application/json" } }
    );
    if (!response.ok) return "";
    const result = (await response.json()) as { accessToken?: string };
    return result.accessToken || "";
  } catch {
    return "";
  }
}

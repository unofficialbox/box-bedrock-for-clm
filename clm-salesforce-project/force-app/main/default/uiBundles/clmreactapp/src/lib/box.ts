import { CLM_CONFIG } from "../config";
import { apexRestUrl } from "./apexRest";

declare global {
  interface Window {
    __CLM_RUNTIME_CONFIG__?: {
      boxAccessToken?: string;
      agentforceAgentId?: string;
      agentforceAppId?: string;
      salesforceOrigin?: string;
    };
  }
}

export interface BoxFolderItem {
  id: string;
  name: string;
  type: string;
  /** Bytes, for the size column. Absent on items Box does not report it for. */
  size?: number;
  modified_at?: string;
  extension?: string;
}

/**
 * List a folder with the downscoped token.
 *
 * Null means the listing failed and the caller should fall back; an empty array means the
 * folder is genuinely empty, which a freshly provisioned contract folder always is. The
 * two must stay distinct -- conflating them renders fixtures over a working workspace and
 * makes a healthy empty folder look like a broken connection.
 *
 * The failure is logged because the fallback is otherwise indistinguishable from a
 * working demo with no files: the page renders fixtures and says nothing. A CORS
 * rejection is the usual cause, and Box reports it in the body as
 * cors_origin_not_whitelisted with the offending origin.
 */
export async function listBoxFolderItems(
  folderId: string,
  accessToken: string,
): Promise<BoxFolderItem[] | null> {
  try {
    const response = await fetch(
      `https://api.box.com/2.0/folders/${encodeURIComponent(folderId)}/items?fields=id,name,type,size,extension,modified_at&limit=100`,
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );
    if (!response.ok) {
      console.warn(
        `[CLM] Box folder listing failed (${response.status}); falling back to fixtures.`,
        await response.text().catch(() => "")
      );
      return null;
    }
    const result = (await response.json()) as { entries?: BoxFolderItem[] };
    return (result.entries || []).filter((entry) => entry.type === "file");
  } catch (error) {
    // A CORS rejection surfaces here as an opaque TypeError with no response to read.
    console.warn("[CLM] Box folder listing threw; check the Box app's CORS domains.", error);
    return null;
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

export interface BoxWorkspaceToken {
  accessToken: string;
  /** The folder the endpoint actually minted for, which may differ from what was asked. */
  folderId: string;
}

const NO_TOKEN: BoxWorkspaceToken = { accessToken: "", folderId: "" };

/**
 * Ask Salesforce for a folder-scoped Box token.
 *
 * A Salesforce record id is the preferred input. The endpoint resolves the folder from
 * the Box for Salesforce package's own record-to-folder association, so the workspace
 * never has to know a Box folder id and one cannot be supplied from the URL. The folder
 * comes back in the response because the caller does not know it up front.
 *
 * `folderId` remains for pages with no record context and for the local harness. It is
 * the reason a page opened without either still shows fixtures rather than failing: the
 * default `demo-workspace` is not numeric and the endpoint rejects it outright.
 */
export async function fetchDownscopedBoxToken(
  context: { folderId: string; salesforceRecordId?: string },
): Promise<BoxWorkspaceToken> {
  const injectedToken = window.__CLM_RUNTIME_CONFIG__?.boxAccessToken;
  if (injectedToken) return { accessToken: injectedToken, folderId: context.folderId };

  const recordId = context.salesforceRecordId;
  const query = recordId
    ? `recordId=${encodeURIComponent(recordId)}`
    : `folderId=${encodeURIComponent(context.folderId)}`;

  try {
    let granted = await requestToken(query, context.folderId);

    // A record with no folder yet is provisioned rather than refused. Provisioning writes
    // the association, and Apex forbids a callout after DML, so the package cannot create
    // the folder and mint a token in one request -- hence provision, then retry.
    if (!granted.accessToken && granted.needsFolder && recordId) {
      const provisioned = await provisionBoxFolder(recordId);
      if (provisioned) {
        granted = await requestToken(query, context.folderId);
      }
    }
    return granted.accessToken ? { accessToken: granted.accessToken, folderId: granted.folderId } : NO_TOKEN;
  } catch (error) {
    console.warn("[CLM] Token endpoint unreachable; falling back to fixtures.", error);
    return NO_TOKEN;
  }
}

interface TokenAttempt extends BoxWorkspaceToken {
  /** The record has no Box folder yet, so provisioning it is worth a try. */
  needsFolder: boolean;
}

async function requestToken(query: string, requestedFolderId: string): Promise<TokenAttempt> {
  const response = await fetch(apexRestUrl(`/services/apexrest/clm/box-token?${query}`), {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    console.warn(`[CLM] Token endpoint returned ${response.status}.`, detail);
    return { ...NO_TOKEN, needsFolder: detail.includes("no_box_folder_mapping") };
  }
  const result = (await response.json()) as { accessToken?: string; folderId?: string };
  return {
    accessToken: result.accessToken || "",
    // Trust the endpoint's folder over the requested one; with a recordId it is the only
    // place the answer exists.
    folderId: result.folderId || requestedFolderId,
    needsFolder: false,
  };
}

/**
 * Ask the Box for Salesforce package to create this record's workspace folder. Returns
 * false rather than throwing, so a workspace that cannot be provisioned falls back to
 * fixtures like every other Box failure here.
 */
async function provisionBoxFolder(recordId: string): Promise<boolean> {
  try {
    const response = await fetch(
      apexRestUrl(`/services/apexrest/clm/box-folder?recordId=${encodeURIComponent(recordId)}`),
      { method: "POST", headers: { Accept: "application/json" } },
    );
    if (!response.ok) {
      console.warn(
        `[CLM] Could not provision a Box folder (${response.status}).`,
        await response.text().catch(() => ""),
      );
      return false;
    }
    return true;
  } catch (error) {
    console.warn("[CLM] Folder provisioning unreachable.", error);
    return false;
  }
}

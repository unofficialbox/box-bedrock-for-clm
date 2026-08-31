import { CLM_CONFIG } from "../config";

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
}

/**
 * List a folder with the downscoped token. Empty on any failure; the caller falls back
 * to synthetic fixtures.
 *
 * The failure is logged because the fallback is otherwise indistinguishable from a
 * working demo with no files: the page renders fixtures and says nothing. A CORS
 * rejection is the usual cause, and Box reports it in the body as
 * cors_origin_not_whitelisted with the offending origin.
 */
export async function listBoxFolderItems(folderId: string, accessToken: string): Promise<BoxFolderItem[]> {
  try {
    const response = await fetch(
      `https://api.box.com/2.0/folders/${encodeURIComponent(folderId)}/items?fields=id,name,type&limit=100`,
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );
    if (!response.ok) {
      console.warn(
        `[CLM] Box folder listing failed (${response.status}); falling back to fixtures.`,
        await response.text().catch(() => "")
      );
      return [];
    }
    const result = (await response.json()) as { entries?: BoxFolderItem[] };
    return (result.entries || []).filter((entry) => entry.type === "file");
  } catch (error) {
    // A CORS rejection surfaces here as an opaque TypeError with no response to read.
    console.warn("[CLM] Box folder listing threw; check the Box app's CORS domains.", error);
    return [];
  }
}

/**
 * Ask Box for a short-lived, iframe-embeddable preview URL for one file.
 *
 * Box renders the document on its own origin and hands back a URL, so the app never
 * loads the Box Content Preview library. That matters here: the library is fetched
 * from cdn01.boxcdn.net, and the Experience Cloud CSP allows only 'self' plus a
 * Salesforce allowlist under script-src -- `CspTrustedSite` has no script-src field
 * that can widen it. It does have `isApplicableToFrameSrc`, so an iframe is the one
 * preview path the platform can actually grant.
 *
 * Requires the `item_preview` scope, which the downscoped token already carries.
 * Empty on any failure; the caller renders a message rather than an empty frame.
 */
export async function fetchBoxEmbedLink(fileId: string, accessToken: string): Promise<string> {
  try {
    const response = await fetch(
      `https://api.box.com/2.0/files/${encodeURIComponent(fileId)}?fields=expiring_embed_link`,
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );
    if (!response.ok) {
      console.warn(
        `[CLM] Box embed link failed (${response.status}); preview unavailable for file ${fileId}.`,
        await response.text().catch(() => "")
      );
      return "";
    }
    const result = (await response.json()) as { expiring_embed_link?: { url?: string } };
    const url = result.expiring_embed_link?.url || "";
    if (!url) {
      // A token without item_preview returns 200 with the field simply absent.
      console.warn(`[CLM] Box returned no embed link for file ${fileId}; check the token scope.`);
    }
    return url;
  } catch (error) {
    console.warn("[CLM] Box embed link threw; check the Box app's CORS domains.", error);
    return "";
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
  const response = await fetch(`/services/apexrest/clm/box-token?${query}`, {
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
      `/services/apexrest/clm/box-folder?recordId=${encodeURIComponent(recordId)}`,
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

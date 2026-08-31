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

export async function fetchDownscopedBoxToken(folderId: string): Promise<string> {
  const injectedToken = window.__CLM_RUNTIME_CONFIG__?.boxAccessToken;
  if (injectedToken) return injectedToken;

  try {
    const response = await fetch(
      `/services/apexrest/clm/box-token?folderId=${encodeURIComponent(folderId)}`,
      { headers: { Accept: "application/json" } }
    );
    if (!response.ok) {
      console.warn(
        `[CLM] Token endpoint returned ${response.status}; falling back to fixtures.`,
        await response.text().catch(() => "")
      );
      return "";
    }
    const result = (await response.json()) as { accessToken?: string };
    return result.accessToken || "";
  } catch (error) {
    console.warn("[CLM] Token endpoint unreachable; falling back to fixtures.", error);
    return "";
  }
}

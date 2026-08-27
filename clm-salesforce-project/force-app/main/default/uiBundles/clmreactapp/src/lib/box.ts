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
      Preview: new () => {
        show(fileId: string, accessToken: string, options: Record<string, unknown>): void;
        hide(): void;
        removeAllListeners(): void;
      };
    };
  }
}

/**
 * Box Content Preview 2.106.0, vendored rather than loaded from cdn01.boxcdn.net.
 * The Experience Cloud CSP grants the Box CDN under style-src, connect-src, and
 * frame-src, but script-src allows only 'self' plus a Salesforce allowlist, and
 * CspTrustedSite has no script-src field to change that. Serving the bundle from
 * the UI bundle itself is the only way the script loads at all.
 */
import previewScriptUrl from "../vendor/box-preview/preview.js?url";
import "../vendor/box-preview/preview.css";

export interface BoxFolderItem {
  id: string;
  name: string;
  type: string;
}

let previewLoader: Promise<boolean> | null = null;

/**
 * Inject the Content Preview bundle once. Resolves false if the script fails to
 * evaluate, so callers fall back to the file list instead of hanging.
 */
export function loadBoxPreview(): Promise<boolean> {
  if (window.Box?.Preview) return Promise.resolve(true);
  if (previewLoader) return previewLoader;

  previewLoader = new Promise<boolean>((resolve) => {
    if (typeof document === "undefined") return resolve(false);

    // preview.css is bundled through the import above; only the script needs injecting.
    const script = document.createElement("script");
    script.src = previewScriptUrl;
    script.async = true;
    script.onload = () => resolve(Boolean(window.Box?.Preview));
    script.onerror = () => resolve(false);
    document.head.appendChild(script);
  });
  return previewLoader;
}

/** List a folder with the downscoped token. Empty on any failure; the caller falls back. */
export async function listBoxFolderItems(folderId: string, accessToken: string): Promise<BoxFolderItem[]> {
  try {
    const response = await fetch(
      `https://api.box.com/2.0/folders/${encodeURIComponent(folderId)}/items?fields=id,name,type&limit=100`,
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );
    if (!response.ok) return [];
    const result = (await response.json()) as { entries?: BoxFolderItem[] };
    return (result.entries || []).filter((entry) => entry.type === "file");
  } catch {
    return [];
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

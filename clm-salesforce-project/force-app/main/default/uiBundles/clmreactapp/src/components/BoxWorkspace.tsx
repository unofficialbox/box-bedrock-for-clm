import { lazy, Suspense, useEffect, useState } from "react";
import { ExternalLink, FileText, FolderOpen, LockKeyhole } from "lucide-react";
import { CLM_CONFIG } from "../config";
import { CONTRACT_FILES } from "../data";
import { fetchDownscopedBoxToken, listBoxFolderItems, type BoxFolderItem } from "../lib/box";

/**
 * Loaded lazily to keep box-ui-elements out of the initial bundle. It is several
 * megabytes, and the synthetic-fixture path never needs it, so the entry chunk stays
 * small for anyone who does not reach live Box content.
 */
const BoxElements = lazy(() =>
  import("./BoxElements").then((module) => ({ default: module.BoxElements })),
);

export function BoxWorkspace({ folderId }: { folderId: string }) {
  const [token, setToken] = useState("");
  const [files, setFiles] = useState<BoxFolderItem[]>([]);
  const [loading, setLoading] = useState(true);

  /**
   * Resolve the governed token, then probe the folder.
   *
   * ContentExplorer fetches its own listing, so this call is a liveness check rather
   * than the source of what gets rendered: it decides between live Box content and the
   * synthetic fixtures, and it logs why when Box refuses.
   */
  useEffect(() => {
    let active = true;
    (async () => {
      const accessToken = await fetchDownscopedBoxToken(folderId);
      if (!active) return;
      setToken(accessToken);
      if (!accessToken) {
        setLoading(false);
        return;
      }
      const entries = await listBoxFolderItems(folderId, accessToken);
      if (!active) return;
      setFiles(entries);
      setLoading(false);
    })();
    return () => {
      active = false;
    };
  }, [folderId]);

  if (loading) {
    return <div className="workspace-state" data-testid="box-loading">Connecting to the governed Box workspace…</div>;
  }

  if (token && files.length > 0) {
    return (
      <section className="box-live" data-testid="box-preview">
        <div className="box-fallback-head">
          <div>
            <span className="eyebrow"><FolderOpen size={15} /> Box workspace</span>
            <h2>{CLM_CONFIG.workspace.name}</h2>
            <p>Browsed from Box with a short-lived token scoped to this folder.</p>
          </div>
          {CLM_CONFIG.workspace.boxUrl ? (
            <a className="secondary-button" href={CLM_CONFIG.workspace.boxUrl} target="_blank" rel="noreferrer">
              Open in Box <ExternalLink size={15} />
            </a>
          ) : null}
        </div>
        <Suspense fallback={<div className="workspace-state">Loading Box elements…</div>}>
          <BoxElements folderId={folderId} token={token} />
        </Suspense>
      </section>
    );
  }

  return (
    <section className="box-fallback" data-testid="box-fallback">
      <div className="box-fallback-head">
        <div>
          <span className="eyebrow"><FolderOpen size={15} /> Box workspace</span>
          <h2>{CLM_CONFIG.workspace.name}</h2>
          <p>Synthetic file fixtures are shown; live content activates when Salesforce supplies a downscoped Box token.</p>
        </div>
        {CLM_CONFIG.workspace.boxUrl ? (
          <a className="secondary-button" href={CLM_CONFIG.workspace.boxUrl} target="_blank" rel="noreferrer">
            Open in Box <ExternalLink size={15} />
          </a>
        ) : null}
      </div>
      <div className="file-list">
        {CONTRACT_FILES.map((file) => {
          const href = CLM_CONFIG.workspace.boxHostname && !file.id.startsWith("demo-")
            ? `https://${CLM_CONFIG.workspace.boxHostname}/file/${file.id}`
            : "";
          const content = (
            <>
            <span className="file-icon"><FileText size={18} /></span>
            <span className="file-copy"><strong>{file.label}</strong><small>{file.name}</small></span>
            <span className={`risk risk-${file.risk.toLowerCase()}`}>{file.risk}</span>
            {href ? <ExternalLink size={15} /> : null}
            </>
          );
          return href ? (
            <a key={file.id} className="file-row" href={href} target="_blank" rel="noreferrer">{content}</a>
          ) : (
            <div key={file.id} className="file-row">{content}</div>
          );
        })}
      </div>
      <div className="secure-note"><LockKeyhole size={15} /> Browser source contains no Box client secret.</div>
    </section>
  );
}

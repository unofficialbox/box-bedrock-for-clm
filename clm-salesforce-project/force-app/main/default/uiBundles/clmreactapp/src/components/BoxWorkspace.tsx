import { useEffect, useRef, useState } from "react";
import { ExternalLink, FileText, FolderOpen, LockKeyhole } from "lucide-react";
import { CLM_CONFIG } from "../config";
import { CONTRACT_FILES } from "../data";
import { fetchDownscopedBoxToken } from "../lib/box";

export function BoxWorkspace({ folderId }: { folderId: string }) {
  const hostRef = useRef<HTMLDivElement>(null);
  const [token, setToken] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    fetchDownscopedBoxToken(folderId)
      .then((value) => { if (active) setToken(value); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [folderId]);

  useEffect(() => {
    if (!token || !hostRef.current || !window.Box?.ContentExplorer) return;
    const explorer = new window.Box.ContentExplorer();
    explorer.show(folderId, token, {
      container: hostRef.current,
      canPreview: true,
      canDownload: false,
      canDelete: false,
      canRename: false,
      canUpload: true,
      canCreateNewFolder: false,
    });
    return () => {
      explorer.removeAllListeners();
      explorer.hide();
    };
  }, [folderId, token]);

  if (loading) {
    return <div className="workspace-state" data-testid="box-loading">Connecting to the governed Box workspace…</div>;
  }

  if (token && window.Box?.ContentExplorer) {
    return <div ref={hostRef} className="box-explorer" data-testid="box-explorer" />;
  }

  return (
    <section className="box-fallback" data-testid="box-fallback">
      <div className="box-fallback-head">
        <div>
          <span className="eyebrow"><FolderOpen size={15} /> Box workspace</span>
          <h2>{CLM_CONFIG.workspace.name}</h2>
          <p>Synthetic file fixtures are shown; previews activate when Salesforce supplies a downscoped Box token.</p>
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

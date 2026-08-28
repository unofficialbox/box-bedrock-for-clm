import { useEffect, useRef, useState } from "react";
import { ExternalLink, FileText, FolderOpen, LockKeyhole } from "lucide-react";
import { CLM_CONFIG } from "../config";
import { CONTRACT_FILES } from "../data";
import { fetchDownscopedBoxToken, listBoxFolderItems, loadBoxPreview, type BoxFolderItem } from "../lib/box";
import { BoxElements } from "./BoxElements";

/** Lead with the redline when the folder has one; that is the contract under review. */
function preferredFile(files: BoxFolderItem[]): BoxFolderItem | null {
  if (!files.length) return null;
  return files.find((file) => /redline/i.test(file.name)) || files[0];
}

export function BoxWorkspace({ folderId }: { folderId: string }) {
  const hostRef = useRef<HTMLDivElement>(null);
  const [token, setToken] = useState("");
  const [files, setFiles] = useState<BoxFolderItem[]>([]);
  const [activeFileId, setActiveFileId] = useState("");
  const [previewReady, setPreviewReady] = useState(false);
  const [loading, setLoading] = useState(true);

  // Resolve the governed token, then the folder contents and the preview bundle.
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
      const [entries, ready] = await Promise.all([
        listBoxFolderItems(folderId, accessToken),
        loadBoxPreview(),
      ]);
      if (!active) return;
      setFiles(entries);
      setPreviewReady(ready);
      setActiveFileId(preferredFile(entries)?.id || "");
      setLoading(false);
    })();
    return () => {
      active = false;
    };
  }, [folderId]);

  // Mount Content Preview on the selected file.
  useEffect(() => {
    if (!token || !activeFileId || !previewReady || !hostRef.current || !window.Box?.Preview) return;
    const preview = new window.Box.Preview();
    preview.show(activeFileId, token, {
      container: hostRef.current,
      showDownload: false,
      showAnnotations: false,
    });
    return () => {
      preview.removeAllListeners();
      preview.hide();
    };
  }, [token, activeFileId, previewReady]);

  if (loading) {
    return <div className="workspace-state" data-testid="box-loading">Connecting to the governed Box workspace…</div>;
  }

  if (token && previewReady && activeFileId) {
    return (
      <section className="box-live" data-testid="box-preview">
        <div className="box-fallback-head">
          <div>
            <span className="eyebrow"><FolderOpen size={15} /> Box workspace</span>
            <h2>{CLM_CONFIG.workspace.name}</h2>
            <p>Previewed from Box with a short-lived token scoped to this folder.</p>
          </div>
          {CLM_CONFIG.workspace.boxUrl ? (
            <a className="secondary-button" href={CLM_CONFIG.workspace.boxUrl} target="_blank" rel="noreferrer">
              Open in Box <ExternalLink size={15} />
            </a>
          ) : null}
        </div>
        <div className="box-preview-layout">
          <nav className="box-file-rail" aria-label="Box files">
            {files.map((file) => (
              <button
                key={file.id}
                className={file.id === activeFileId ? "file-row file-row-active" : "file-row"}
                onClick={() => setActiveFileId(file.id)}
              >
                <span className="file-icon"><FileText size={18} /></span>
                <span className="file-copy"><strong>{file.name}</strong></span>
              </button>
            ))}
          </nav>
          <div ref={hostRef} className="box-preview-host" data-testid="box-preview-host" />
        </div>
        <div className="secure-note"><LockKeyhole size={15} /> Browser source contains no Box client secret.</div>
        <BoxElements folderId={folderId} token={token} />
      </section>
    );
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

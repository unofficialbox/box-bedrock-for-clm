import { lazy, Suspense, useEffect, useRef, useState } from "react";
import { WorkspaceSkeleton } from "./WorkspaceSkeleton";
import { ExternalLink, FileText, FolderOpen } from "lucide-react";
import { CLM_CONFIG } from "../config";
import { CONTRACT_FILES } from "../data";
import { fetchDownscopedBoxToken, listBoxFolderItems, type BoxFolderItem, type ClmPageContext } from "../lib/box";

/**
 * Loaded lazily to keep box-ui-elements out of the initial bundle. It is several
 * megabytes, and the synthetic-fixture path never needs it, so the entry chunk stays
 * small for anyone who does not reach live Box content.
 */
const BoxElements = lazy(() =>
  import("./BoxElements").then((module) => ({ default: module.BoxElements })),
);

export function BoxWorkspace({
  context,
  onFilesLoaded,
  onBoxReady,
  reloadKey,
  onUpload,
}: {
  context: ClmPageContext;
  /**
   * Hands the loaded listing up so the timeline beside this panel is built from the same
   * array, already filtered. A second fetch could disagree with what the table shows.
   */
  onFilesLoaded?: (files: BoxFolderItem[]) => void;
  /**
   * Hands up the minted token and the folder it is bound to, so the workspace can offer
   * an upload without this panel owning the button. Null while there is no live Box.
   */
  onBoxReady?: (box: { token: string; folderId: string } | null) => void;
  /** Change this to re-list the folder -- after an upload, say. */
  reloadKey?: number;
  /** Opens the upload dialog, which the workspace owns. */
  onUpload?: () => void;
}) {
  const [token, setToken] = useState("");
  const [folderId, setFolderId] = useState("");
  const [files, setFiles] = useState<BoxFolderItem[] | null>(null);
  const [loading, setLoading] = useState(true);
  /**
   * Held in a ref, not a dependency. The prop is optional, so a caller passing an inline
   * function would otherwise change identity every render and refetch the folder in a
   * loop.
   */
  const notifyFiles = useRef(onFilesLoaded);
  useEffect(() => {
    notifyFiles.current = onFilesLoaded;
  }, [onFilesLoaded]);
  const notifyBox = useRef(onBoxReady);
  useEffect(() => {
    notifyBox.current = onBoxReady;
  }, [onBoxReady]);

  /**
   * Resolve the governed token, then probe the folder.
   *
   * The folder is an output, not an input: with a record id the endpoint reads the Box
   * for Salesforce association and tells us which folder it minted for. Everything below
   * uses that answer rather than anything the URL supplied.
   *
   * The listing does double duty: it decides between live Box content and the synthetic
   * fixtures (and logs why when Box refuses), and it is the table the workspace renders,
   * so the folder is read once rather than once per component.
   */
  useEffect(() => {
    let active = true;
    (async () => {
      const granted = await fetchDownscopedBoxToken(context);
      if (!active) return;
      setToken(granted.accessToken);
      setFolderId(granted.folderId);
      if (!granted.accessToken) {
        setLoading(false);
        return;
      }
      const entries = await listBoxFolderItems(granted.folderId, granted.accessToken);
      if (!active) return;
      setFiles(entries);
      notifyFiles.current?.(entries || []);
      notifyBox.current?.(
        granted.accessToken && granted.folderId
          ? { token: granted.accessToken, folderId: granted.folderId }
          : null,
      );
      setLoading(false);
    })();
    return () => {
      active = false;
    };
  }, [context, reloadKey]);

  if (loading) {
    return <WorkspaceSkeleton />;
  }

  // A token plus a listing that came back is live content, even when the folder is empty.
  // A newly provisioned contract folder has no files yet and is still the real workspace.
  if (token && files !== null) {
    return (
      <section className="box-live" data-testid="box-preview">
        <div className="box-fallback-head">
          <div>
            <h2>{CLM_CONFIG.workspace.name}</h2>
          </div>
          {CLM_CONFIG.workspace.boxUrl ? (
            <a className="secondary-button" href={CLM_CONFIG.workspace.boxUrl} target="_blank" rel="noreferrer">
              Open in Box <ExternalLink size={15} />
            </a>
          ) : null}
        </div>
        <Suspense fallback={<div className="workspace-state">Loading Box elements…</div>}>
          <BoxElements folderId={folderId} token={token} files={files} onUpload={onUpload} />
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
    </section>
  );
}

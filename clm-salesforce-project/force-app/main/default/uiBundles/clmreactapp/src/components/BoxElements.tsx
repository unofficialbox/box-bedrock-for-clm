import { useState } from "react";
import { FolderOpen, LockKeyhole, Upload } from "lucide-react";
import ContentExplorer from "box-ui-elements/es/elements/content-explorer";
import ContentUploader from "box-ui-elements/es/elements/content-uploader";
import "box-ui-elements/dist/explorer.css";
import "box-ui-elements/dist/uploader.css";

/**
 * Box UI Elements mounted on the same downscoped token the preview uses.
 *
 * These are the npm React components rather than the prebuilt standalone bundles.
 * The standalone builds embed their own React, which would run a second React
 * instance alongside the app's; importing keeps one React and lets Vite code-split.
 *
 * Both elements are bounded by the token, not by these props: the token is scoped to
 * one folder and to base_explorer,item_preview,item_read,item_upload, so the browser
 * cannot reach content outside the governed workspace even if a prop is wrong.
 */
export function BoxElements({ folderId, token }: { folderId: string; token: string }) {
  const [uploaderOpen, setUploaderOpen] = useState(false);
  // Remount the explorer after an upload so the new item appears without a reload.
  const [refreshKey, setRefreshKey] = useState(0);

  if (!token || !folderId) {
    return null;
  }

  return (
    <section className="box-elements" data-testid="box-elements">
      <div className="box-fallback-head">
        <div>
          <span className="eyebrow"><FolderOpen size={15} /> Box workspace</span>
          <h2>Contract folder</h2>
          <p>Browse and add contract documents in Box, scoped to this folder.</p>
        </div>
        <button
          type="button"
          className="secondary-button"
          onClick={() => setUploaderOpen((open) => !open)}
          data-testid="box-uploader-toggle"
        >
          <Upload size={15} /> {uploaderOpen ? "Close uploader" : "Add documents"}
        </button>
      </div>

      {uploaderOpen ? (
        <div className="box-element-host" data-testid="box-content-uploader">
          <ContentUploader
            token={token}
            rootFolderId={folderId}
            onComplete={() => {
              setRefreshKey((key) => key + 1);
              setUploaderOpen(false);
            }}
            onClose={() => setUploaderOpen(false)}
          />
        </div>
      ) : null}

      <div className="box-element-host" data-testid="box-content-explorer">
        <ContentExplorer
          key={refreshKey}
          token={token}
          rootFolderId={folderId}
          canPreview
          canUpload
          canCreateNewFolder={false}
          canDelete={false}
          canRename={false}
          canShare={false}
          canDownload={false}
        />
      </div>

      <div className="secure-note">
        <LockKeyhole size={15} /> Browser source contains no Box client secret; the token is
        scoped to this folder.
      </div>
    </section>
  );
}

import { useState } from "react";
import { IntlProvider } from "react-intl";
import { LockKeyhole, Upload } from "lucide-react";
import ContentExplorer, { type BoxItem } from "box-ui-elements/es/elements/content-explorer";
import ContentUploader from "box-ui-elements/es/elements/content-uploader";
import "box-ui-elements/dist/explorer.css";
import "box-ui-elements/dist/uploader.css";
import { BoxDocumentPreview } from "./BoxDocumentPreview";

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
  const [selected, setSelected] = useState<BoxItem | null>(null);

  if (!token || !folderId) {
    return null;
  }

  return (
    // box-ui-elements components read from react-intl context and throw
    // "Could not find required `intl` object" without a provider above them. Empty
    // messages fall back to each component's defaultMessage, which is English.
    <IntlProvider locale="en" messages={{}}>
    <section className="box-elements" data-testid="box-elements">
      {/* No heading here: BoxWorkspace already renders the folder header above. */}
      <div className="box-elements-toolbar">
        <button
          type="button"
          className="secondary-button"
          onClick={() => setUploaderOpen((open) => !open)}
          data-testid="box-uploader-toggle"
        >
          <Upload size={15} /> {uploaderOpen ? "Close uploader" : "Add documents"}
        </button>
      </div>

      {selected ? (
        <BoxDocumentPreview
          key={selected.id}
          fileId={selected.id}
          fileName={selected.name}
          token={token}
          onClose={() => setSelected(null)}
        />
      ) : null}

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
          // The explorer's own preview stays off: it loads Box Content Preview from
          // cdn01.boxcdn.net, which the Experience Cloud CSP blocks under script-src --
          // the wall cf3b54a hit. Selecting a file opens BoxDocumentPreview instead,
          // which embeds Box's own rendering in an iframe and needs no library here.
          canPreview={false}
          onSelect={(items) => {
            const file = items.find((item) => item.type === "file");
            if (file) setSelected(file);
          }}
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
    </IntlProvider>
  );
}

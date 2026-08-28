import { useState } from "react";
import { IntlProvider } from "react-intl";
import { LockKeyhole, Upload } from "lucide-react";
import ContentExplorer from "box-ui-elements/es/elements/content-explorer";
import ContentUploader from "box-ui-elements/es/elements/content-uploader";
import BoxPreview, { type BoxFile, type BoxToken, type PreviewOptions } from "box-content-preview";

/**
 * Box Content Preview, wired to serve its runtime assets from our own origin.
 *
 * The class is imported and bundled, so nothing is script-loaded and no CDN is involved
 * -- which matters because Experience Cloud CSP allows only 'self' under script-src and
 * worker-src. But the viewers still fetch assets at runtime (the pdf.js worker, CMaps,
 * per-type third-party code), and those default to cdn01.boxcdn.net. Overriding
 * staticBaseURI on every show() points them at public/box-preview, staged from
 * node_modules by scripts/stage-box-preview-assets.mjs.
 *
 * Without it the viewer mounts but cannot render: pdf.js fails with
 * "Cannot read properties of undefined (reading 'GlobalWorkerOptions')".
 *
 * This lives here rather than in lib/box.ts because that module is on the entry path;
 * importing the library there pulled several megabytes into the initial chunk. This
 * module is lazy-loaded behind the live Box branch.
 */
class LocalAssetPreview extends BoxPreview {
  show(fileIdOrFile: string | BoxFile, token: BoxToken, options: PreviewOptions = {}): void {
    super.show(fileIdOrFile, token, {
      ...options,
      staticBaseURI: new URL("box-preview/", document.baseURI).href,
    });
  }
}

/**
 * Hand the library to box-ui-elements at module load, before any element checks for it.
 * ContentPreview tests `!!global.Box && !!global.Box.Preview` and, finding it, skips its
 * own script injection entirely -- so it never reaches the CDN.
 */
const previewReady = ((): boolean => {
  if (typeof window === "undefined") return false;

  // box-content-preview's exports map does not expose dist/lib/index.css, so the
  // stylesheet is served from the staged assets rather than imported.
  const href = new URL("box-preview/index.css", document.baseURI).href;
  if (!document.head.querySelector(`link[href="${href}"]`)) {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = href;
    document.head.appendChild(link);
  }

  window.Box = { ...(window.Box || {}), Preview: LocalAssetPreview };
  return true;
})();
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
          canPreview={previewReady}
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

import { useEffect, useState } from "react";
import { IntlProvider } from "react-intl";
import { Eye } from "lucide-react";
import ContentExplorer from "box-ui-elements/es/elements/content-explorer";
import "box-ui-elements/dist/explorer.css";
import { BoxDocumentPreview } from "./BoxDocumentPreview";
import { listBoxFolderItems, type BoxFolderItem } from "../lib/box";

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
  const [selected, setSelected] = useState<BoxFolderItem | null>(null);
  const [folderInView, setFolderInView] = useState(folderId);
  const [previewable, setPreviewable] = useState<BoxFolderItem[]>([]);

  /**
   * Track the files in whichever folder the explorer is showing, so the picker offers
   * the documents the user is actually looking at.
   *
   * The picker exists because ContentExplorer will not surrender a file click on its
   * own terms. Its ItemList only calls onItemClick for a file when `canPreview` is on,
   * and turning that on also mounts its preview dialog, which has no library to load
   * here and fails to a "Sad Box Cloud" modal. There is no prop that separates the two,
   * so the trigger lives outside the explorer.
   */
  useEffect(() => {
    let active = true;
    listBoxFolderItems(folderInView, token).then((items) => {
      // Null is a failed listing; an empty folder is simply nothing to preview.
      if (active) setPreviewable(items ?? []);
    });
    return () => {
      active = false;
    };
  }, [folderInView, token]);

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
        {previewable.length > 0 ? (
          <label className="box-preview-picker">
            <Eye size={15} />
            <span className="visually-hidden">Preview a document</span>
            <select
              value={selected?.id || ""}
              onChange={(event) => {
                const file = previewable.find((item) => item.id === event.target.value);
                setSelected(file || null);
              }}
              data-testid="box-preview-picker"
            >
              <option value="">Preview a document…</option>
              {previewable.map((file) => (
                <option key={file.id} value={file.id}>
                  {file.name}
                </option>
              ))}
            </select>
          </label>
        ) : null}

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

      <div className="box-element-host" data-testid="box-content-explorer">
        <ContentExplorer
          token={token}
          rootFolderId={folderId}
          // Must stay off. It loads Box Content Preview from cdn01.boxcdn.net, which the
          // Experience Cloud CSP blocks under script-src -- the wall cf3b54a hit -- and
          // the dialog then renders a "Sad Box Cloud" error over the workspace.
          canPreview={false}
          // Follow the explorer so the picker lists the folder on screen.
          onNavigate={(item) => {
            setFolderInView(item.id);
            // A preview from the previous folder should not outlive the navigation.
            setSelected(null);
          }}
          canUpload
          canCreateNewFolder={false}
          canDelete={false}
          canRename={false}
          canShare={false}
          canDownload={false}
        />
      </div>
    </section>
    </IntlProvider>
  );
}

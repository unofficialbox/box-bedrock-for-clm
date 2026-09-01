import { IntlProvider } from "react-intl";
import BoxAnnotations from "box-annotations";
import ContentExplorer from "box-ui-elements/es/elements/content-explorer";
import "box-ui-elements/dist/explorer.css";

/**
 * Box UI Elements mounted on the downscoped token.
 *
 * These are the npm React components rather than the prebuilt standalone bundles. The
 * standalone builds embed their own React, which would run a second React instance
 * alongside the app's; importing keeps one React and lets Vite code-split.
 *
 * The explorer is left to do its own job. It already provides preview, upload, download,
 * rename, delete, share and folder creation, so the app adds no affordances of its own --
 * an earlier preview picker and embed panel duplicated what the element gives for free.
 *
 * What the browser may actually do is bounded by the token, not by these props: it is
 * scoped to one folder and to the scopes ClmBoxTokenService requests. A prop enables a
 * control; the scope decides whether Box honours it.
 */
/**
 * ContentPreview expects a BoxAnnotations instance and does not construct one, so preview
 * silently does nothing without it. ContentExplorer forwards contentPreviewProps straight
 * to the preview element, which is how it reaches there.
 *
 * Built once at module scope rather than per render: it is stateful, and a fresh instance
 * on every render would discard the annotator between previews.
 */
const boxAnnotations = new BoxAnnotations({});

export function BoxElements({ folderId, token }: { folderId: string; token: string }) {
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
        <div className="box-element-host" data-testid="box-content-explorer">
          <ContentExplorer
            token={token}
            rootFolderId={folderId}
            // On by request, and known to fail on this surface: the element's preview
            // loads Box Content Preview from cdn01.boxcdn.net, which an Experience Cloud
            // site cannot allow -- script-src is 'self' plus a Salesforce allowlist, and
            // CspTrustedSite has no script-src field to widen it. Clicking a file throws
            // "Invariant failed" inside box-ui-elements and renders "We're sorry,
            // something went wrong" where the preview should be.
            canPreview
            contentPreviewProps={{ boxAnnotations }}
            canUpload
            canCreateNewFolder
            canDelete
            canRename
            canShare
            canDownload
          />
        </div>
      </section>
    </IntlProvider>
  );
}

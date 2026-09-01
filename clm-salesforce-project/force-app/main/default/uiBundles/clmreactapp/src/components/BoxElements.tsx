import { IntlProvider } from "react-intl";
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
            // Off, and not by preference. The element's preview loads Box Content Preview
            // from cdn01.boxcdn.net, and an Experience Cloud site cannot allow that:
            // script-src is 'self' plus a Salesforce allowlist, and CspTrustedSite has no
            // script-src field to widen it -- the object has no such column at all.
            // Enabled, clicking a file throws "Invariant failed" inside box-ui-elements
            // and the panel renders "We're sorry, something went wrong".
            canPreview={false}
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

import { useEffect, useState } from "react";
import { FileText, X } from "lucide-react";
import { fetchBoxEmbedLink } from "../lib/box";

/**
 * Renders one Box document inline.
 *
 * Box previews the file on its own origin and returns an expiring URL, so nothing about
 * the document format is this app's problem and no preview library ships in the bundle.
 * See `fetchBoxEmbedLink` for why an iframe is the only preview path the Experience
 * Cloud CSP can grant.
 */
export function BoxDocumentPreview({
  fileId,
  fileName,
  token,
  onClose,
}: {
  fileId: string;
  fileName: string;
  token: string;
  onClose: () => void;
}) {
  const [embedUrl, setEmbedUrl] = useState("");
  const [loading, setLoading] = useState(true);

  // Keyed by file id at the call site, so a different file remounts with fresh state
  // rather than resetting it here -- setting state synchronously in an effect body
  // cascades renders, and the lint rule rejects it.
  useEffect(() => {
    let active = true;
    fetchBoxEmbedLink(fileId, token).then((url) => {
      if (!active) return;
      setEmbedUrl(url);
      setLoading(false);
    });
    return () => {
      active = false;
    };
  }, [fileId, token]);

  return (
    <div className="box-document-preview" data-testid="box-document-preview">
      <div className="box-preview-head">
        <span className="box-preview-title">
          <FileText size={16} /> {fileName}
        </span>
        <button type="button" className="secondary-button" onClick={onClose} aria-label="Close preview">
          <X size={15} /> Close
        </button>
      </div>

      {loading ? (
        <div className="workspace-state" data-testid="box-preview-loading">
          Requesting a preview link from Box…
        </div>
      ) : embedUrl ? (
        <iframe
          className="box-preview-frame"
          src={embedUrl}
          title={`Box preview of ${fileName}`}
          data-testid="box-preview-frame"
          allowFullScreen
        />
      ) : (
        // Distinguished from an empty frame on purpose: a blank preview reads as a
        // broken demo, and the cause is almost always CSP or token scope.
        <div className="workspace-state" data-testid="box-preview-unavailable">
          Box did not return a preview link for this file. Check the browser console, the
          token scope, and that the Box app domain is a trusted site for frame-src.
        </div>
      )}
    </div>
  );
}

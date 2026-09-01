import { FileText } from "lucide-react";
import type { BoxFolderItem } from "../lib/box";

function formatSize(bytes?: number): string {
  if (bytes == null) return "—";
  if (bytes >= 1_048_576) return `${(bytes / 1_048_576).toFixed(1)} MB`;
  if (bytes >= 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${bytes} B`;
}

function formatModified(iso?: string): string {
  if (!iso) return "—";
  const at = new Date(iso);
  return Number.isNaN(at.getTime())
    ? "—"
    : at.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
}

/**
 * The contract package, listed from the governed folder.
 *
 * Hand-rolled rather than a Content Explorer. The element never emitted a file
 * activation in this embedding -- it renders in its small/touch mode regardless of width,
 * and its ItemList only opens a file when `!isTouch` -- so preview could not be reached
 * through it. Listing the folder ourselves and mounting ContentPreview directly is the
 * pattern the qualitypilot reference uses, and it puts the click in our hands.
 */
export function BoxDocumentTable({
  files,
  onSelect,
}: {
  files: BoxFolderItem[];
  onSelect: (file: BoxFolderItem) => void;
}) {
  if (files.length === 0) {
    return (
      <div className="workspace-state" data-testid="box-table-empty">
        There are no documents in this folder yet.
      </div>
    );
  }

  return (
    <table className="box-table" data-testid="box-document-table">
      <thead>
        <tr>
          <th scope="col">Name</th>
          <th scope="col">Modified</th>
          <th scope="col">Size</th>
        </tr>
      </thead>
      <tbody>
        {files.map((file) => (
          <tr
            key={file.id}
            data-testid="box-table-row"
          >
            <td>
              {/* A button, not a row handler: the file name is the thing you activate,
                  and it stays reachable from the keyboard. */}
              <button type="button" className="box-table-name" onClick={() => onSelect(file)}>
                <FileText size={16} aria-hidden="true" />
                <span>{file.name}</span>
              </button>
            </td>
            <td>{formatModified(file.modified_at)}</td>
            <td>{formatSize(file.size)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

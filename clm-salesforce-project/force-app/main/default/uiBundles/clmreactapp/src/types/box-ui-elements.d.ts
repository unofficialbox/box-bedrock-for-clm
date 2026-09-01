/**
 * box-ui-elements ships Flow types, not TypeScript, so `tsc -b` cannot resolve these
 * modules on its own. Declare only the props this app actually passes; a wider surface
 * would be guesswork against an untyped package.
 */
declare module "box-ui-elements/es/elements/content-explorer" {
  import type { ComponentType } from "react";

  export interface BoxItem {
    id: string;
    name: string;
    type: "file" | "folder" | "web_link";
  }

  export interface ContentExplorerProps {
    token: string;
    rootFolderId: string;
    currentFolderId?: string;
    canUpload?: boolean;
    canDownload?: boolean;
    canDelete?: boolean;
    canRename?: boolean;
    canShare?: boolean;
    canCreateNewFolder?: boolean;
    canPreview?: boolean;
    /** Fires with the folder the explorer navigated into. */
    onNavigate?: (item: BoxItem) => void;
    /**
     * Forwarded verbatim to the ContentPreview element. It is how a BoxAnnotations
     * instance reaches preview, which does not build one itself.
     */
    contentPreviewProps?: Record<string, unknown>;
    onUpload?: (items: BoxItem[]) => void;
    language?: string;
  }

  const ContentExplorer: ComponentType<ContentExplorerProps>;
  export default ContentExplorer;
}

declare module "box-ui-elements/es/elements/content-uploader" {
  import type { ComponentType } from "react";

  export interface UploadedItem {
    id: string;
    name: string;
    type: string;
  }

  export interface ContentUploaderProps {
    token: string;
    rootFolderId: string;
    fileLimit?: number;
    onComplete?: (items: UploadedItem[]) => void;
    onClose?: () => void;
    onError?: (error: unknown) => void;
    language?: string;
  }

  const ContentUploader: ComponentType<ContentUploaderProps>;
  export default ContentUploader;
}

declare module "box-ui-elements/dist/explorer.css";
declare module "box-ui-elements/dist/uploader.css";

/** box-annotations ships no types; the app only ever constructs it. */
declare module "box-annotations" {
  export default class BoxAnnotations {
    constructor(options?: Record<string, unknown>);
  }
}

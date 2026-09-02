const boxHostname = (import.meta.env.VITE_BOX_HOSTNAME || "").replace(/^https?:\/\//, "").replace(/\/$/, "");
const workspaceFolderId = import.meta.env.VITE_BOX_FOLDER_ID || "demo-workspace";

export const CLM_CONFIG = {
  site: {
    /**
     * Where a signed-out visitor signs in. Site-specific and not derivable: the app path
     * serves this bundle for every URL beneath it, so `/login` under it renders the app
     * rather than a sign-in page. Left blank, the signed-out state simply offers no link.
     */
    loginUrl: import.meta.env.VITE_CLM_LOGIN_URL || "",
  },
  workspace: {
    name: "CLM-2026-Northstar",
    folderId: workspaceFolderId,
    boxHostname,
    boxUrl: boxHostname && workspaceFolderId !== "demo-workspace"
      ? `https://${boxHostname}/folder/${workspaceFolderId}`
      : "",
    boxAppUrl: import.meta.env.VITE_BOX_APP_URL || "",
    boxFormUrl: import.meta.env.VITE_BOX_FORM_URL || "",
  },
  folders: {
    redlines: import.meta.env.VITE_BOX_REDLINES_FOLDER_ID || "",
    approvals: import.meta.env.VITE_BOX_APPROVALS_FOLDER_ID || "",
    signature: import.meta.env.VITE_BOX_SIGNATURE_FOLDER_ID || "",
    obligations: import.meta.env.VITE_BOX_OBLIGATIONS_FOLDER_ID || "",
    docgen: import.meta.env.VITE_BOX_DOCGEN_FOLDER_ID || "",
  },
} as const;

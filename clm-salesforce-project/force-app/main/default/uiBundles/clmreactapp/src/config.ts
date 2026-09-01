const boxHostname = (import.meta.env.VITE_BOX_HOSTNAME || "").replace(/^https?:\/\//, "").replace(/\/$/, "");
const workspaceFolderId = import.meta.env.VITE_BOX_FOLDER_ID || "demo-workspace";

export const CLM_CONFIG = {
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
  agentforce: {
    // The agent's 18-digit id, not its developer name. The Agentforce API rejects the
    // developer name outright -- "CLM_Contract_Copilot is not a valid agent ID" -- so
    // there is no portable default to ship; the id is per-org and supplied at build time
    // or through runtime config. Find it with:
    //   sf data query -q "SELECT Id, DeveloperName FROM BotDefinition"
    agentId: import.meta.env.VITE_AGENTFORCE_AGENT_ID || "",
    appId: import.meta.env.VITE_AGENTFORCE_APP_ID || "",
    salesforceOrigin: import.meta.env.VITE_SALESFORCE_ORIGIN || "",
    // The shipped agent is defined by an Agent Script authoring bundle, which is what
    // "file-based" means to the conversation client. Set this to "false" when pointing
    // VITE_AGENTFORCE_AGENT_ID at an agent built in Agent Builder instead.
    fileBased: (import.meta.env.VITE_AGENTFORCE_FILE_BASED || "true") !== "false",
  },
} as const;

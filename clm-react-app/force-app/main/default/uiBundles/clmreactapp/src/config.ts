export const CLM_CONFIG = {
  workspace: {
    name: "CLM-2026-Northstar",
    folderId: "399081692991",
    boxUrl: "https://kadams.ent.box.com/folder/399081692991",
    boxAppUrl: "https://kadams.ent.box.com/app/KyZohNNwCy6Y6ccmn",
    boxFormUrl: "https://kadams.ent.box.com/f/c83f2ab35ee74a519b5fbc2859e2a858",
  },
  folders: {
    redlines: "399080778184",
    approvals: "399082072259",
    signature: "399081939679",
    obligations: "399081567921",
    docgen: "399363530207",
  },
  agentforce: {
    agentId: import.meta.env.VITE_AGENTFORCE_AGENT_ID || "",
    appId: import.meta.env.VITE_AGENTFORCE_APP_ID || "",
    salesforceOrigin: import.meta.env.VITE_SALESFORCE_ORIGIN || "",
  },
} as const;

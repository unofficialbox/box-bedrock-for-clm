import { useCallback, useEffect, useMemo, useState } from "react";
import { FileStack, LayoutDashboard, Upload } from "lucide-react";
import { BoxWorkspace } from "./components/BoxWorkspace";
import { DocumentTimeline } from "./components/DocumentTimeline";
import { UploadDialog } from "./components/UploadDialog";
import { WorkspaceMetrics } from "./components/WorkspaceMetrics";
import { ContractList } from "./components/ContractList";
import type { BoxFolderItem } from "./lib/box";
import { formatDealValue, type ClmContractSummary } from "./lib/contracts";
import { getClmPageContext } from "./lib/box";

/**
 * This app is the counterparty's surface, and only theirs.
 *
 * It carries no agent. The Copilot that used to sit beside this content ran as its own
 * agent user rather than as the person signed in, and took the contract it answered about
 * from the conversation -- so the one control on the page that could be asked anything was
 * the one control none of the scoping reached. Everything a counterparty would ask it
 * ("is it signed", "what did we agree", "what do you need from me") is already on the page,
 * and everything it could reach that they cannot -- redlines, the approved clause library,
 * our fallback positions -- is the reason not to put it here.
 *
 * It used to serve both sides, which is why it carried a redline review queue and a "copy
 * agent context" button. The internal persona now works headlessly through the MCP server,
 * so everything here is what an external party may see: their own contracts, the documents
 * in them, and the Copilot. Anything that reveals Acme's own process does not belong.
 */
type View = "contracts" | "workspace";

/**
 * The query string a selected contract should produce.
 *
 * `folderId` is what the workspace needs and `recordId` is the fallback the endpoint
 * resolves from, so both are written when known; `contractId` is there to make the URL
 * readable. Selecting a contract has to change the URL, or the workspace cannot be
 * linked to, reloaded, or reached with the back button.
 */
function contractSearch(contract: ClmContractSummary): string {
  const params = new URLSearchParams();
  if (contract.contractId) params.set("contractId", contract.contractId);
  if (contract.recordId) params.set("recordId", contract.recordId);
  if (contract.boxFolderId) params.set("folderId", contract.boxFolderId);
  return params.toString();
}

export function Workspace() {
  const [context, setContext] = useState(() => getClmPageContext());
  const [selected, setSelected] = useState<ClmContractSummary | null>(null);
  /**
   * Null until the folder has been listed. An empty array means the folder is genuinely
   * empty, and the history panel says something different for each.
   */
  const [files, setFiles] = useState<BoxFolderItem[] | null>(null);
  /** The live Box token and folder, once the workspace panel has minted them. */
  const [box, setBox] = useState<{ token: string; folderId: string } | null>(null);
  const [uploading, setUploading] = useState(false);
  /** Bumped on upload close so the folder is listed again and the new file appears. */
  const [reloadKey, setReloadKey] = useState(0);
  /**
   * A record in the URL means the page was opened with context -- a Lightning or
   * Experience page bound to one contract -- so it goes straight to that workspace.
   * Without one there is nothing to show yet, and the dashboard is the entry point.
   */
  const [view, setView] = useState<View>(context.salesforceRecordId ? "workspace" : "contracts");

  /**
   * Keep the app in step with the address bar. Without this, Back after opening a
   * contract changes the URL and leaves the workspace on screen. The URL is the
   * authority here: going back re-reads it and drops the row selection, so the folder in
   * the URL is what the workspace opens.
   */
  useEffect(() => {
    function syncToUrl() {
      const params = new URLSearchParams(window.location.search);
      const namesAContract = params.has("recordId") || params.has("folderId");
      setContext(getClmPageContext());
      setSelected(null);
      setFiles(null);
      setView(namesAContract ? "workspace" : "contracts");
    }
    window.addEventListener("popstate", syncToUrl);
    return () => window.removeEventListener("popstate", syncToUrl);
  }, []);

  const openContract = useCallback((contract: ClmContractSummary) => {
    const search = contractSearch(contract);
    setFiles(null);
    window.history.pushState({}, "", search ? `?${search}` : window.location.pathname);
    setSelected(contract);
    setView("workspace");
  }, []);

  /**
   * Which Box folder the workspace opens.
   *
   * The record id wins when there is one. The Box for Salesforce package owns the
   * record-to-folder association and provisions a folder for a record that has none, so
   * asking by record is both authoritative and self-healing; Box_Workspace_Folder_ID__c
   * is a denormalised copy that can fall behind it.
   *
   * A folder id is used only when there is no record to ask about -- a deep link or the
   * local harness -- and that path is still bounded by Allowed_Folder_Ids__c, because
   * there the caller chose the folder rather than a record.
   */
  const workspaceContext = useMemo(() => {
    if (selected?.recordId) {
      return { ...context, salesforceRecordId: selected.recordId };
    }
    return {
      ...context,
      ...(selected?.boxFolderId ? { folderId: selected.boxFolderId } : {}),
    };
  }, [context, selected]);


  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand"><span className="brand-mark">A</span><span><strong>Acme Contracts</strong><small>Box-powered CLM</small></span></div>
        <nav aria-label="Primary">
          <button className={view === "contracts" ? "nav-active" : ""} onClick={() => setView("contracts")}><FileStack size={16} /> Your contracts</button>
          <button className={view === "workspace" ? "nav-active" : ""} onClick={() => setView("workspace")}><LayoutDashboard size={16} /> Workspace</button>
        </nav>
      </header>

      {/*
        The banner describes the contract that is open, and nothing else.

        It used to fall back to a fixture whenever none was selected, so the list view was
        headed by another contract's name, value and term -- and by "Approval blocked",
        which contradicted the status on the row directly beneath it. A header stating
        different facts from the list under it is worse than no header.

        The Salesforce record ID came out of the eyebrow at the same time. It is internal
        plumbing, and this page faces the counterparty.
      */}
      {selected ? (
        <div className="contract-banner">
          <div>
            <span className="eyebrow">{selected.contractId}</span>
            <h1>{selected.name}</h1>
            <p>{[selected.counterparty, selected.contractType].filter(Boolean).join(" · ")}</p>
          </div>
          <div className="banner-metrics">
            <Metric label="Value" value={formatDealValue(selected.dealValue)} />
            {selected.termMonths != null ? (
              <Metric label="Term" value={`${selected.termMonths} months`} />
            ) : null}
            {selected.status ? <Metric label="Status" value={selected.status} /> : null}
          </div>
        </div>
      ) : null}

      {view === "workspace" ? (
        <div className="workspace-metrics-row">
          <WorkspaceMetrics files={files} />
        </div>
      ) : null}

      <div className={`content-grid${view === "workspace" ? " content-grid-aside" : ""}`}>
        <main>
          {view === "contracts" ? (
            <ContractList onSelect={openContract} />
          ) : (
            <BoxWorkspace
              context={workspaceContext}
              onFilesLoaded={setFiles}
              onBoxReady={setBox}
              reloadKey={reloadKey}
            />
          )}
        </main>
        {view === "workspace" ? (
          <>
            {/* Its own grid row, so the action sits above the right-hand panel while both
                panels still start on the same line. Nesting it with the timeline pushed
                that panel down and left the table stranded a button's height above it. */}
            {box ? (
              <div className="workspace-actions">
                <button
                  type="button"
                  className="upload-button"
                  onClick={() => setUploading(true)}
                  data-testid="box-upload-open"
                >
                  <Upload size={15} /> Upload document
                </button>
              </div>
            ) : null}
            <DocumentTimeline files={files} />
          </>
        ) : null}
      </div>
      {uploading && box ? (
        <UploadDialog
          folderId={box.folderId}
          tokenProvider={() => box.token}
          onClose={() => {
            setUploading(false);
            setReloadKey((n) => n + 1);
          }}
        />
      ) : null}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="metric"><span>{label}</span><strong>{value}</strong></div>;
}

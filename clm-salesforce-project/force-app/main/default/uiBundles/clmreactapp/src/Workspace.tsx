import { useCallback, useEffect, useMemo, useState } from "react";
import { FileStack, LayoutDashboard } from "lucide-react";
import { BoxWorkspace } from "./components/BoxWorkspace";
import { DocumentTimeline } from "./components/DocumentTimeline";
import { UploadDialog } from "./components/UploadDialog";
import { WorkspaceMetrics } from "./components/WorkspaceMetrics";
import { ContractList } from "./components/ContractList";
import { ProfileMenu } from "./components/ProfileMenu";
import { fetchIdentity, type ClmIdentity } from "./lib/identity";
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
function viewFromSearch(search = window.location.search): View {
  const params = new URLSearchParams(search);
  // An explicit marker wins: the list is reachable with a contract still named in the URL,
  // so returning to it does not throw away which contract was open.
  if (params.get("view") === "contracts") return "contracts";
  return params.has("recordId") || params.has("folderId") ? "workspace" : "contracts";
}

/** The same query the page already carries, with the view marker set or cleared. */
function searchForView(view: View): string {
  const params = new URLSearchParams(window.location.search);
  if (view === "contracts") params.set("view", "contracts");
  else params.delete("view");
  const search = params.toString();
  return search ? `?${search}` : window.location.pathname;
}

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
  /** Set when Box cannot be read at all, so nothing derived from the listing is drawn. */
  const [boxError, setBoxError] = useState("");
  /** Who is signed in. Null until the answer arrives; nothing is drawn before then. */
  const [identity, setIdentity] = useState<ClmIdentity | null>(null);
  const [uploading, setUploading] = useState(false);
  /** Bumped on upload close so the folder is listed again and the new file appears. */
  const [reloadKey, setReloadKey] = useState(0);
  /**
   * A record in the URL means the page was opened with context -- a Lightning or
   * Experience page bound to one contract -- so it goes straight to that workspace.
   * Without one there is nothing to show yet, and the dashboard is the entry point.
   */
  const [view, setView] = useState<View>(() => viewFromSearch());

  /**
   * Keep the app in step with the address bar. Without this, Back after opening a
   * contract changes the URL and leaves the workspace on screen. The URL is the
   * authority here: going back re-reads it and drops the row selection, so the folder in
   * the URL is what the workspace opens.
   */
  useEffect(() => {
    function syncToUrl() {
      setContext(getClmPageContext());
      setSelected(null);
      setFiles(null);
      setBoxError("");
      setView(viewFromSearch());
    }
    window.addEventListener("popstate", syncToUrl);
    return () => window.removeEventListener("popstate", syncToUrl);
  }, []);

  useEffect(() => {
    let active = true;
    (async () => {
      const who = await fetchIdentity();
      if (active && who.ok) setIdentity(who.value);
    })();
    return () => {
      active = false;
    };
  }, []);

  const openContract = useCallback((contract: ClmContractSummary) => {
    const search = contractSearch(contract);
    setFiles(null);
    setBoxError("");
    window.history.pushState({}, "", search ? `?${search}` : window.location.pathname);
    setSelected(contract);
    setView("workspace");
  }, []);

  /**
   * Switching tabs is a navigation, so it goes through the address bar.
   *
   * Without this the view changed and the URL did not, so a reload re-read the contract
   * still named there and dropped the reader back into the workspace they had just left.
   * The contract stays in the query when the list is shown, which is what lets the
   * Workspace tab return to it rather than becoming a dead control.
   */
  const showView = useCallback((next: View) => {
    window.history.pushState({}, "", searchForView(next));
    setView(next);
  }, []);

  /**
   * Which Box folder the workspace opens.
   *
   * The record id wins when there is one. The Box for Salesforce package owns the
   * record-to-folder association and provisions a folder for a record that has none, so
   * asking by record is both authoritative and self-healing; Box_Workspace_Folder_ID__c
   * is a denormalised copy that can fall behind it.
   *
   * A record is the only way in. The endpoint no longer accepts a caller-named folder at
   * all, so a folder id here only labels what came back.
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
        <div className="brand"><span className="brand-mark">A</span><span><strong>Acme Vendor Portal</strong><small>CLM powered by Box and Headless 360</small></span></div>
        <nav aria-label="Primary">
          <button className={view === "contracts" ? "nav-active" : ""} onClick={() => showView("contracts")}><FileStack size={16} /> Your contracts</button>
          <button className={view === "workspace" ? "nav-active" : ""} onClick={() => showView("workspace")}><LayoutDashboard size={16} /> Workspace</button>
        </nav>
        <ProfileMenu identity={identity} />
      </header>

      {/*
        The banner describes the contract that is open, and only while it is open.

        The selection survives a trip to the list -- that is what lets the Workspace tab
        return to it -- so the banner has to be gated on the view as well. Without that it
        headed the list of every contract with the name, value and term of one of them.

        It used to fall back to a fixture whenever none was selected, so the list view was
        headed by another contract's name, value and term -- and by "Approval blocked",
        which contradicted the status on the row directly beneath it. A header stating
        different facts from the list under it is worse than no header.

        The Salesforce record ID came out of the eyebrow at the same time. It is internal
        plumbing, and this page faces the counterparty.
      */}
      {selected && view === "workspace" ? (
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

      {view === "workspace" && !boxError ? (
        <div className="workspace-metrics-row">
          <WorkspaceMetrics files={files} />
        </div>
      ) : null}

      <div className={`content-grid${view === "workspace" && !boxError ? " content-grid-aside" : ""}`}>
        <main>
          {view === "contracts" ? (
            <ContractList onSelect={openContract} signInUrl={identity?.loginUrl} />
          ) : (
            <BoxWorkspace
              context={workspaceContext}
              onFilesLoaded={setFiles}
              onBoxReady={setBox}
              reloadKey={reloadKey}
              onUpload={() => setUploading(true)}
              onFailed={setBoxError}
            />
          )}
        </main>
        {view === "workspace" && !boxError ? <DocumentTimeline files={files} /> : null}
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

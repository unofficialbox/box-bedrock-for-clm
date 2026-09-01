import { useCallback, useEffect, useMemo, useState } from "react";
import { FileStack, LayoutDashboard } from "lucide-react";
import { AgentforcePanel } from "./components/AgentforcePanel";
import { BoxWorkspace } from "./components/BoxWorkspace";
import { ContractList } from "./components/ContractList";
import { formatDealValue, type ClmContractSummary } from "./lib/contracts";
import { getClmPageContext } from "./lib/box";

/**
 * This app is the counterparty's surface, and only theirs.
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
      setView(namesAContract ? "workspace" : "contracts");
    }
    window.addEventListener("popstate", syncToUrl);
    return () => window.removeEventListener("popstate", syncToUrl);
  }, []);

  const openContract = useCallback((contract: ClmContractSummary) => {
    const search = contractSearch(contract);
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

      <div className="content-grid">
        <main>
          {view === "contracts" ? (
            <ContractList onSelect={openContract} />
          ) : (
            <BoxWorkspace context={workspaceContext} />
          )}
        </main>
        <AgentforcePanel contractId={selected?.contractId || context.contractId} />
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="metric"><span>{label}</span><strong>{value}</strong></div>;
}

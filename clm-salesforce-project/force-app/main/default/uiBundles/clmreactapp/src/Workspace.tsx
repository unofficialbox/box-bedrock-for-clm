import { useCallback, useEffect, useMemo, useState } from "react";
import { FileStack, LayoutDashboard } from "lucide-react";
import { AgentforcePanel } from "./components/AgentforcePanel";
import { BoxWorkspace } from "./components/BoxWorkspace";
import { ContractList } from "./components/ContractList";
import { formatDealValue, type ClmContractSummary } from "./lib/contracts";
import { NORTHSTAR_CONTRACT } from "./data";
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

      <div className="contract-banner">
        <div><span className="eyebrow">{selected?.contractId || context.contractId}{workspaceContext.salesforceRecordId ? ` · Salesforce ${workspaceContext.salesforceRecordId}` : ""}</span><h1>{selected?.name || NORTHSTAR_CONTRACT.name}</h1><p>{[selected?.counterparty || NORTHSTAR_CONTRACT.counterparty, selected?.contractType || NORTHSTAR_CONTRACT.contractType].join(" · ")}</p></div>
        <div className="banner-metrics">
          <Metric label="Value" value={selected ? formatDealValue(selected.dealValue) : NORTHSTAR_CONTRACT.value} />
          <Metric label="Term" value={selected?.termMonths != null ? `${selected.termMonths} months` : NORTHSTAR_CONTRACT.term} />
          <Metric label="Status" value={selected?.status || NORTHSTAR_CONTRACT.status} warning />
        </div>
      </div>

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

function Metric({ label, value, danger, warning }: { label: string; value: string; danger?: boolean; warning?: boolean }) {
  return <div className="metric"><span>{label}</span><strong className={danger ? "danger" : warning ? "warning" : ""}>{value}</strong></div>;
}

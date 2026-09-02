import { useEffect, useState } from "react";
import { FileStack, ShieldAlert } from "lucide-react";
import { fetchClmContracts, formatDealValue, type ClmContractSummary } from "../lib/contracts";
import { PortfolioCharts } from "./PortfolioCharts";
import { formatDate } from "../lib/documents";
import { fetchContractsViaGraphql } from "../lib/contractsGraphql";
import { NORTHSTAR_CONTRACT } from "../data";

/** Stands in when no org is behind the page, so the dashboard is never empty. */
const FIXTURE_ROWS: ClmContractSummary[] = [
  {
    recordId: "",
    contractId: NORTHSTAR_CONTRACT.id,
    name: NORTHSTAR_CONTRACT.name,
    counterparty: NORTHSTAR_CONTRACT.counterparty,
    contractType: NORTHSTAR_CONTRACT.contractType,
    status: NORTHSTAR_CONTRACT.status,
  },
];

export function ContractList({ onSelect }: { onSelect: (contract: ClmContractSummary) => void }) {
  const [contracts, setContracts] = useState<ClmContractSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [live, setLive] = useState(false);
  const [source, setSource] = useState<"graphql" | "apex" | "fixture">("fixture");

  /**
   * GraphQL first, Apex second.
   *
   * The UI API runs as the logged-in user, so the platform enforces sharing and field
   * security rather than a hand-written projection. It is preferred wherever it is
   * available. `null` means the surface does not offer it, which is distinct from an
   * empty result -- a user who can genuinely see no contracts must not silently fall
   * through to the Apex endpoint and get a different answer.
   */
  useEffect(() => {
    let active = true;
    (async () => {
      const viaGraphql = await fetchContractsViaGraphql();
      const viaApex = viaGraphql === null ? await fetchClmContracts() : null;
      const rows = viaGraphql ?? viaApex;
      if (!active) return;
      // Null from both means nothing answered, so the fixture stands in. An empty array
      // is an org with no contracts yet -- a real answer, and shown as one.
      setSource(rows === null ? "fixture" : viaGraphql ? "graphql" : "apex");
      setLive(rows !== null);
      setContracts(rows ?? FIXTURE_ROWS);
      setLoading(false);
    })();
    return () => {
      active = false;
    };
  }, []);

  if (loading) {
    return <div className="workspace-state" data-testid="contracts-loading">Loading contract records…</div>;
  }

  return (
    <>
      {/* Above the list, because the portfolio question ("what state is all this in") is
          asked before the record question ("which one do I open"). */}
      {live ? <PortfolioCharts contracts={contracts} /> : null}
      <section className="contract-list-card" data-testid="contracts-view" data-source={source}>
      {/*
        No heading. The nav already says which view this is, and the sentence under it
        described the page to someone who is looking at it -- the charts above and the
        columns below say more, in less space. The fixture warning stays, because that one
        tells the reader something the page cannot otherwise show.
      */}
      {live && contracts.length === 0 ? (
        <div className="workspace-state" data-testid="contracts-empty">
          No contract records yet. Creating one in Salesforce brings it here.
        </div>
      ) : (
        <table className="box-table contract-table" data-testid="contract-table">
          <thead>
            <tr>
              <th scope="col">Contract</th>
              <th scope="col">Signed by</th>
              <th scope="col">Value</th>
              <th scope="col">Term ends</th>
              <th scope="col">Status</th>
            </tr>
          </thead>
          <tbody>
            {contracts.map((contract, index) => (
              <tr key={contract.recordId || `fixture-${index}`} data-testid="contract-row">
                <td>
                  {/* A button, not a row handler: the contract name is the thing you
                      activate, and it stays reachable from the keyboard. */}
                  <button
                    type="button"
                    className="box-table-name"
                    onClick={() => onSelect(contract)}
                    data-testid="contract-open"
                  >
                    <FileStack size={15} aria-hidden="true" />
                    <span className="cell-stack">
                      <span>{contract.name || contract.contractId || "Untitled contract"}</span>
                      <small>{contract.contractId}</small>
                    </span>
                  </button>
                </td>
                <td className="cell-type">
                  <span className="cell-stack">
                    <span>{contract.counterpartyEntity || contract.counterparty || "—"}</span>
                    {contract.counterpartyEntity && contract.counterparty ? (
                      <small>{contract.counterparty}</small>
                    ) : null}
                  </span>
                </td>
                <td className="cell-number">
                  {contract.dealValue != null ? formatDealValue(contract.dealValue) : "—"}
                </td>
                <td className="cell-number">{formatDate(contract.endDate)}</td>
                <td>
                  {contract.status ? <span className="status-pill">{contract.status}</span> : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {!live ? (
        <div className="secure-note" data-testid="contracts-fixture-note">
          <ShieldAlert size={15} /> No Salesforce contract records were returned; the workspace
          will fall back to synthetic Box fixtures.
        </div>
      ) : null}
      </section>
    </>
  );
}

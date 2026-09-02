import { useEffect, useState } from "react";
import { ChevronRight, FileStack, ShieldAlert } from "lucide-react";
import { fetchClmContracts, formatDealValue, type ClmContractSummary } from "../lib/contracts";
import { PortfolioCharts } from "./PortfolioCharts";
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
      <div className="section-heading">
        <div>
          <span className="eyebrow"><FileStack size={15} /> Contract records</span>
          <h2>Your contracts</h2>
          <p>
            {/*
              This page faces a counterparty, so it says what they are looking at rather
              than how it was fetched. Which rows appear is decided by Salesforce sharing
              for the signed-in user, not by anything here -- an admin sees every contract
              and a counterparty sees only their own, from the same code.
            */}
            {live
              ? "Contracts your organisation is party to. Open one to read its documents."
              : "Synthetic fixture shown; the live list activates when Salesforce is reachable."}
          </p>
        </div>
      </div>

      {live && contracts.length === 0 ? (
        <div className="workspace-state" data-testid="contracts-empty">
          No contract records yet. Creating one in Salesforce brings it here.
        </div>
      ) : null}

      <div className="contract-rows">
        {contracts.map((contract, index) => (
          <button
            type="button"
            key={contract.recordId || `fixture-${index}`}
            className="contract-row"
            onClick={() => onSelect(contract)}
            data-testid="contract-row"
          >
            <span className="contract-copy">
              <strong>{contract.name || contract.contractId || "Untitled contract"}</strong>
              <small>
                {[contract.contractId, contract.counterparty, contract.contractType]
                  .filter(Boolean)
                  .join(" · ")}
              </small>
            </span>
            <span className="contract-meta">
              {contract.dealValue != null ? <span className="contract-value">{formatDealValue(contract.dealValue)}</span> : null}
              {contract.status ? <span className="status-pill">{contract.status}</span> : null}
            </span>
            <ChevronRight size={16} />
          </button>
        ))}
      </div>

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

import { useEffect, useState } from "react";
import { ChevronRight, FileStack, ShieldAlert } from "lucide-react";
import { fetchClmContracts, formatDealValue, type ClmContractSummary } from "../lib/contracts";
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
    riskLevel: NORTHSTAR_CONTRACT.risk,
  },
];

export function ContractList({ onSelect }: { onSelect: (contract: ClmContractSummary) => void }) {
  const [contracts, setContracts] = useState<ClmContractSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [live, setLive] = useState(false);

  useEffect(() => {
    let active = true;
    fetchClmContracts().then((rows) => {
      if (!active) return;
      setLive(rows.length > 0);
      setContracts(rows.length > 0 ? rows : FIXTURE_ROWS);
      setLoading(false);
    });
    return () => {
      active = false;
    };
  }, []);

  if (loading) {
    return <div className="workspace-state" data-testid="contracts-loading">Loading contract records…</div>;
  }

  return (
    <section className="contract-list-card" data-testid="contracts-view">
      <div className="section-heading">
        <div>
          <span className="eyebrow"><FileStack size={15} /> Contract records</span>
          <h2>CLM contracts</h2>
          <p>
            {live
              ? "Read from Salesforce. Opening one resolves its Box folder from the Box for Salesforce record mapping."
              : "Synthetic fixture shown; the live list activates when Salesforce is reachable."}
          </p>
        </div>
      </div>

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
              {contract.riskLevel ? (
                <span className={`risk risk-${contract.riskLevel.toLowerCase()}`}>{contract.riskLevel}</span>
              ) : null}
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
  );
}

import { useCallback, useEffect, useState } from "react";
import { FileStack } from "lucide-react";
import { NOT_AUTHENTICATED, fetchClmContracts, formatDealValue, type ClmContractSummary } from "../lib/contracts";
import { PortfolioCharts } from "./PortfolioCharts";
import { DataError } from "./DataError";
import { ContractsSkeleton } from "./WorkspaceSkeleton";
import { formatDate } from "../lib/documents";
import { CLM_CONFIG } from "../config";
import { fetchContractsViaGraphql } from "../lib/contractsGraphql";

export function ContractList({ onSelect }: { onSelect: (contract: ClmContractSummary) => void }) {
  const [contracts, setContracts] = useState<ClmContractSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [source, setSource] = useState<"graphql" | "apex">("apex");
  const [attempt, setAttempt] = useState(0);

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
      setLoading(true);
      const viaGraphql = await fetchContractsViaGraphql();
      if (!active) return;
      if (viaGraphql !== null) {
        setSource("graphql");
        setContracts(viaGraphql);
        setError("");
        setLoading(false);
        return;
      }
      // Only when the UI API is not offered here. An empty array from it is a real answer
      // and must not be retried through a different projection.
      const viaApex = await fetchClmContracts();
      if (!active) return;
      setSource("apex");
      setError(viaApex.ok ? "" : viaApex.error);
      setContracts(viaApex.ok ? viaApex.value : []);
      setLoading(false);
    })();
    return () => {
      active = false;
    };
  }, [attempt]);

  const retry = useCallback(() => setAttempt((n) => n + 1), []);

  if (loading) {
    return <ContractsSkeleton />;
  }

  // Nothing is drawn over a failure. A list of contracts is a claim about what this
  // organisation is party to, and inventing one is worse than saying it cannot be read.
  // Being signed out is not a failure to report, it is a door to point at.
  if (error === NOT_AUTHENTICATED) {
    return (
      <DataError
        title="Sign in to see your contracts"
        detail="Your session has ended. Signing in again brings back the contracts your organisation is party to."
        signInUrl={CLM_CONFIG.site.loginUrl}
        onRetry={retry}
        testId="contracts-signed-out"
      />
    );
  }

  if (error) {
    return (
      <DataError
        title="Your contracts could not be loaded"
        detail={error}
        onRetry={retry}
        testId="contracts-error"
      />
    );
  }

  return (
    <>
      {/* Above the list, because the portfolio question ("what state is all this in") is
          asked before the record question ("which one do I open"). */}
      <PortfolioCharts contracts={contracts} />
      <section className="contract-list-card" data-testid="contracts-view" data-source={source}>
      {/*
        No heading. The nav already says which view this is, and the sentence under it
        described the page to someone who is looking at it -- the charts above and the
        columns below say more, in less space.
      */}
      {contracts.length === 0 ? (
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
            {contracts.map((contract) => (
              <tr key={contract.recordId} data-testid="contract-row">
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
      </section>
    </>
  );
}

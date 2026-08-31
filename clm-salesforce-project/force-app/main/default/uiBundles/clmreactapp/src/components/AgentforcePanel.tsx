import { useEffect, useRef } from "react";
import { Bot, ShieldCheck } from "lucide-react";
import { embedAgentforceClient } from "@salesforce/agentforce-conversation-client";
import { CLM_CONFIG } from "../config";
import { AGENT_PROMPTS } from "../data";

export function AgentforcePanel() {
  const hostRef = useRef<HTMLDivElement>(null);
  const initializedRef = useRef(false);
  const runtime = window.__CLM_RUNTIME_CONFIG__;
  const agentId = runtime?.agentforceAgentId || CLM_CONFIG.agentforce.agentId;
  const appId = runtime?.agentforceAppId || CLM_CONFIG.agentforce.appId;

  // Salesforce injects SFDC_ENV into a UI bundle at runtime. origin and basePath are the
  // two things the conversation client cannot work out for itself.
  const sfdcEnv = (globalThis as { SFDC_ENV?: { origin?: string; basePath?: string } }).SFDC_ENV;
  /**
   * The current origin is a fallback only when SFDC_ENV proves we are on-platform. An
   * Experience site sets basePath but leaves origin undefined, so without this the panel
   * shows a placeholder on a site that could host the conversation. Off-platform -- a
   * standalone build, a test, the local harness -- there is no org behind the page, and
   * defaulting to the current origin would attempt an embed that cannot work.
   */
  const salesforceOrigin =
    runtime?.salesforceOrigin ||
    sfdcEnv?.origin ||
    CLM_CONFIG.agentforce.salesforceOrigin ||
    (sfdcEnv ? window.location.origin : "");

  /**
   * An Experience Cloud site is served under a path prefix -- this one is /clm -- and the
   * client builds its endpoints from it. Without a prefix it calls the wrong paths on a
   * site and the panel stays empty, so this is not optional once the app leaves Lightning.
   */
  const sitePrefix = sfdcEnv?.basePath ? sfdcEnv.basePath.replace(/\/+$/, "") : undefined;

  useEffect(() => {
    // appId is optional: it is a Lightning Out 2.0 app id, and the client only needs one
    // for apps created after Spring '26. agentId and an origin are what it cannot do
    // without, so gating the embed on appId kept the placeholder up for no reason.
    if (!hostRef.current || !agentId || !salesforceOrigin || initializedRef.current) return;
    initializedRef.current = true;
    embedAgentforceClient({
      container: hostRef.current,
      salesforceOrigin,
      ...(appId ? { appId } : {}),
      ...(sitePrefix ? { sitePrefix } : {}),
      agentforceClientConfig: {
        agentId,
        agentLabel: "Contract Copilot",
        renderingConfig: { mode: "inline", width: "100%", height: "100%", headerEnabled: false },
        styleTokens: {
          headerBlockBackground: "#071b33",
          containerBackground: "#f8fafc",
          messageBlockOutboundBackgroundColor: "#1166e8",
          messageBlockOutboundTextColor: "#ffffff",
          messageBlockInboundBackgroundColor: "#e9f1ff",
          inboundMessageTextColor: "#071b33",
        },
      },
      onReady: () => {
        console.info("[CLM] Agentforce conversation ready.");
      },
      // Logged for the same reason the Box paths log: the placeholder and a failed embed
      // look identical from outside, so a silent failure reads as "not configured yet".
      onError: (error: { type?: string; detail?: unknown }) => {
        console.warn(`[CLM] Agentforce embed failed (${error?.type ?? "unknown"}).`, error?.detail);
        initializedRef.current = false;
      },
    });
  }, [agentId, appId, salesforceOrigin, sitePrefix]);

  return (
    <aside className="agent-panel" aria-label="Contract Copilot">
      <div className="agent-heading">
        <div className="agent-title"><Bot size={19} /> Contract Copilot</div>
        <span className="live-pill">Agentforce</span>
      </div>
      {agentId && salesforceOrigin ? (
        <div ref={hostRef} className="agent-host" data-testid="agentforce-host" />
      ) : (
        <div className="agent-placeholder" data-testid="agentforce-placeholder">
          <div className="agent-shield"><ShieldCheck size={23} /></div>
          <strong>Human-controlled contract review</strong>
          <p>Set the Agentforce agent id and Salesforce origin to activate chat. The recommended CLM prompts are ready:</p>
          <ul>
            {AGENT_PROMPTS.map((prompt) => <li key={prompt}>{prompt}</li>)}
          </ul>
        </div>
      )}
    </aside>
  );
}

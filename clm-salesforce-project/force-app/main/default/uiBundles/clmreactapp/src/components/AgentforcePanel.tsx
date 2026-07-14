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
  const salesforceOrigin =
    runtime?.salesforceOrigin ||
    (globalThis as { SFDC_ENV?: { origin?: string } }).SFDC_ENV?.origin ||
    CLM_CONFIG.agentforce.salesforceOrigin;

  useEffect(() => {
    if (!hostRef.current || !agentId || !appId || !salesforceOrigin || initializedRef.current) return;
    initializedRef.current = true;
    embedAgentforceClient({
      container: hostRef.current,
      salesforceOrigin,
      appId,
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
      onError: () => {
        initializedRef.current = false;
      },
    });
  }, [agentId, appId, salesforceOrigin]);

  return (
    <aside className="agent-panel" aria-label="Contract Copilot">
      <div className="agent-heading">
        <div className="agent-title"><Bot size={19} /> Contract Copilot</div>
        <span className="live-pill">Agentforce</span>
      </div>
      {agentId && appId && salesforceOrigin ? (
        <div ref={hostRef} className="agent-host" data-testid="agentforce-host" />
      ) : (
        <div className="agent-placeholder" data-testid="agentforce-placeholder">
          <div className="agent-shield"><ShieldCheck size={23} /></div>
          <strong>Human-controlled contract review</strong>
          <p>Configure the Agentforce runtime IDs to activate chat. The recommended CLM prompts are ready:</p>
          <ul>
            {AGENT_PROMPTS.map((prompt) => <li key={prompt}>{prompt}</li>)}
          </ul>
        </div>
      )}
    </aside>
  );
}

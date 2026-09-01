import { useEffect, useRef } from "react";
import { Bot, ShieldCheck } from "lucide-react";
import { embedAgentforceClient } from "@salesforce/agentforce-conversation-client";
/** Box's own stack, so the conversation matches the file list beside it. */
const BOX_FONT_STACK = "Lato, 'Helvetica Neue', Helvetica, Arial, sans-serif";

import { CLM_CONFIG } from "../config";
import { sfdcEnv } from "../lib/sfdcEnv";
import { AGENT_PROMPTS } from "../data";

/**
 * The conversation panel.
 *
 * `contractId` is the only contract awareness the client allows. ACC has no API for
 * seeding agent variables or sending an utterance -- `embedAgentforceClient` takes no
 * context option, the mounted `runtime_copilot-acc-sdk-wrapper` exposes no methods, and
 * the `open`/`close`/`execute` API is `lightning/accApi`, importable only from an LWC
 * inside Lightning. The agent declares `contractId`, `contractRecordId` and `boxFolderId`
 * as variables, but nothing here can set them, which is why the workspace offers "Copy
 * agent context" for the person to paste. Naming the contract in the label and the input
 * is what is left.
 */
export function AgentforcePanel({ contractId }: { contractId?: string }) {
  const hostRef = useRef<HTMLDivElement>(null);
  const initializedRef = useRef(false);
  const runtime = window.__CLM_RUNTIME_CONFIG__;
  const agentId = runtime?.agentforceAgentId || CLM_CONFIG.agentforce.agentId;
  const appId = runtime?.agentforceAppId || CLM_CONFIG.agentforce.appId;
  const fileBased = CLM_CONFIG.agentforce.fileBased;

  // Salesforce injects SFDC_ENV into a UI bundle at runtime.
  const env = sfdcEnv();
  /**
   * The current origin is a fallback only when SFDC_ENV proves we are on-platform. An
   * Experience site sets basePath but leaves origin undefined, so without this the panel
   * shows a placeholder on a site that could host the conversation. Off-platform -- a
   * standalone build, a test, the local harness -- there is no org behind the page, and
   * defaulting to the current origin would attempt an embed that cannot work.
   */
  /**
   * The org's Lightning origin, from SFDC_ENV.orgUrl.
   *
   * Not the site origin. An app-container Experience site serves the React app for every
   * path beneath its prefix, so Lightning Out asking the site for /clm/lightning-out gets
   * the SPA shell back, fails to start, and retries -- a console loop that creates no
   * iframe. sitePrefix still tells it which site context to run in.
   */
  const salesforceOrigin =
    runtime?.salesforceOrigin || env?.orgUrl || CLM_CONFIG.agentforce.salesforceOrigin;

  /**
   * sitePrefix is deliberately not passed.
   *
   * The client treats it and the origin as alternatives. With a prefix it builds
   * `<origin><sitePrefix>/lightning-out`; without one it builds
   * `<origin>/lwr/application/amd/0/ai/lightningout%2Fcontainer`. Since the origin here is
   * the org, passing the prefix asks the org for a site path -- which redirects to the
   * Lightning home page, so the iframe never loads and the client retries forever.
   *
   * The org endpoint is the one that answers; verified by loading it directly.
   */

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
      agentforceClientConfig: {
        agentId,
        // Required for an agent defined by an authoring bundle. Without it the client
        // resolves the agent the Agent Builder way, finds nothing, and mounts an empty
        // panel rather than reporting an error.
        ...(fileBased ? { isFileBased: true } : {}),
        agentLabel: contractId ? `Contract Copilot — ${contractId}` : "Contract Copilot",
        // Config is read once, at mount: the element carries it as a plain property that
        // the Lightning Out proxy reads when it hydrates, and a later assignment records
        // no `_propertyChanged_configuration` and never crosses the frame. So these are
        // fixed for the life of an embed, and the effect re-runs to change them.
        messageInputPlaceholderText: contractId
          ? `Ask about ${contractId}…`
          : "Ask about this contract…",
        renderingConfig: { mode: "inline", width: "100%", height: "100%", headerEnabled: false },
        /**
         * The conversation renders inside the client's own shadow tree, so page CSS
         * cannot reach it -- these tokens are the only styling hook. The font stack is
         * Box's own, so the two panels read as one interface rather than
         * two products side by side.
         */
        styleTokens: {
          headerBlockBackground: "#071b33",
          containerBackground: "#f8fafc",
          messageBlockOutboundBackgroundColor: "#1166e8",
          messageBlockOutboundTextColor: "#ffffff",
          messageBlockInboundBackgroundColor: "#e9f1ff",
          inboundMessageTextColor: "#071b33",

          headerBlockFontFamily: BOX_FONT_STACK,
          headerBlockFontSize: "14px",
          welcomeBlockFontFamily: BOX_FONT_STACK,
          welcomeBlockFontSize: "13px",
          welcomeBlockLineHeight: "1.5",
          messageBlockFontSize: "13px",
          messageBlockLineHeight: "1.5",

          // A single-line input by default; it grows only as far as this.
          messageInputFontSize: "13px",
          messageInputLineHeight: "1.4",
          messageInputMaxHeight: "72px",
          messageInputPadding: "8px 10px",
          messageInputTextPadding: "6px 8px",
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

    // The embed owns an iframe and a Lightning Out application. Emptying the host tears
    // both down, so re-running for a new contract replaces the conversation rather than
    // stacking a second one underneath it.
    const host = hostRef.current;
    return () => {
      host.replaceChildren();
      initializedRef.current = false;
    };
  }, [agentId, appId, salesforceOrigin, fileBased, contractId]);

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

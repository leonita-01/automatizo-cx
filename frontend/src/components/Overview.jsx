import {
  ArrowRight,
  Bot,
  CheckCircle2,
  Clock3,
  Headphones,
  Layers3,
  ShieldCheck,
  Sparkles,
  Zap,
} from "lucide-react";

import MetricCard from "./MetricCard";


export default function Overview({ stats, health, onNavigate }) {
  const maximumIntent = Math.max(...(stats.top_intents || []).map((item) => item.count), 1);
  return (
    <>
      <section className="metrics-grid">
        <MetricCard icon={Bot} label="Conversations" value={stats.total_conversations} helper="Persisted, privacy-safe turns" />
        <MetricCard icon={Zap} label="Automation rate" value={`${stats.automation_rate}%`} helper="Resolved without agent intervention" tone="blue" />
        <MetricCard icon={Clock3} label="Average latency" value={`${stats.average_latency_ms} ms`} helper="End-to-end orchestration" tone="violet" />
        <MetricCard icon={Headphones} label="Open handoffs" value={stats.open_handoffs} helper="Awaiting human review" tone="amber" />
      </section>

      <section className="overview-grid">
        <article className="panel platform-card">
          <div className="platform-copy"><span className="section-kicker"><Sparkles size={14} /> ENTERPRISE CX ORCHESTRATION</span><h2>Automate routine support.<br />Escalate with context.</h2><p>A bilingual, knowledge-grounded assistance layer that evaluates confidence, protects customer data and hands complex work to people.</p><div className="hero-actions"><button className="primary-button" onClick={() => onNavigate("assistant")}>Open AI Assistant <ArrowRight size={16} /></button><button className="secondary-button" onClick={() => onNavigate("knowledge")}>Manage knowledge</button></div></div>
          <div className="orchestration-visual"><div className="flow-node customer">Customer request</div><span>↓</span><div className="flow-row"><div className="flow-node">PII redaction</div><div className="flow-node">Security policy</div></div><span>↓</span><div className="flow-node accent">Grounded orchestration</div><span>↓</span><div className="flow-row"><div className="flow-node success">Automated answer</div><div className="flow-node warning">Agent handoff</div></div></div>
        </article>

        <article className="panel status-card">
          <div className="panel-heading"><div><span className="heading-icon"><Layers3 size={20} /></span><div><h2>Platform readiness</h2><p>Runtime capability checks</p></div></div><span className={`status-badge ${health.status === "healthy" ? "healthy" : "degraded"}`}>{health.status || "checking"}</span></div>
          <ul className="readiness-list">
            <li><CheckCircle2 size={16} /><div><strong>API orchestration</strong><small>FastAPI {health.version || "2.0.0"}</small></div></li>
            <li><CheckCircle2 size={16} /><div><strong>Knowledge database</strong><small>{health.database || "checking"}</small></div></li>
            <li><ShieldCheck size={16} /><div><strong>Security controls</strong><small>PII, injection and admin policy</small></div></li>
            <li><CheckCircle2 size={16} /><div><strong>Integration layer</strong><small>Webhook and n8n ready</small></div></li>
          </ul>
        </article>

        <article className="panel intent-card">
          <div className="panel-heading"><div><div><h2>Top customer intents</h2><p>Live distribution from operational data</p></div></div></div>
          <div className="intent-bars">
            {(stats.top_intents || []).length === 0 ? <div className="empty-state compact"><Bot size={25} /><strong>No conversation data</strong><p>Run a few assistant scenarios to populate this view.</p></div> : stats.top_intents.map((item) => (
              <div key={item.intent}><div><span>{item.intent.replaceAll("_", " ")}</span><strong>{item.count}</strong></div><div className="bar-track"><i style={{ width: `${Math.round(item.count / maximumIntent * 100)}%` }} /></div></div>
            ))}
          </div>
        </article>

        <article className="panel governance-card">
          <span className="section-kicker"><ShieldCheck size={14} /> RESPONSIBLE AUTOMATION</span>
          <h2>Designed for controlled customer operations</h2>
          <div className="governance-points"><p><strong>01</strong><span><b>Grounded responses</b><small>Answers trace back to approved articles.</small></span></p><p><strong>02</strong><span><b>Human accountability</b><small>Risk and low confidence trigger escalation.</small></span></p><p><strong>03</strong><span><b>Privacy controls</b><small>Raw personal data is never stored.</small></span></p></div>
        </article>
      </section>
    </>
  );
}

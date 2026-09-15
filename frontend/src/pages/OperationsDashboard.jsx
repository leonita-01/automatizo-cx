import { useCallback, useEffect, useState } from "react";

import ChatPanel from "../components/ChatPanel";
import HandoffQueue from "../components/HandoffQueue";
import KnowledgeCenter from "../components/KnowledgeCenter";
import Overview from "../components/Overview";
import ProcessAnalyzer from "../components/ProcessAnalyzer";
import { api } from "../services/api";


const VIEW_TITLES = {
  overview: ["Operations Command Center", "Monitor automation performance and platform readiness"],
  assistant: ["AI Assistance Workspace", "Test bilingual voice and chat journeys with explainable routing"],
  knowledge: ["Knowledge Governance", "Create, review and import approved customer-support content"],
  automation: ["Process Automation Assessment", "Evaluate value, complexity and risk before automating"],
  handoffs: ["Human Operations", "Review escalations, integration delivery and security audit events"],
};


const EMPTY_STATS = {
  total_conversations: 0,
  automated_conversations: 0,
  escalated_conversations: 0,
  automation_rate: 0,
  average_confidence: 0,
  average_latency_ms: 0,
  open_handoffs: 0,
  top_intents: [],
};


export default function OperationsDashboard({ activeView, onNavigate }) {
  const [stats, setStats] = useState(EMPTY_STATS);
  const [health, setHealth] = useState({ status: "checking" });
  const [lastUpdated, setLastUpdated] = useState(null);

  const refresh = useCallback(async () => {
    try {
      const [analytics, healthStatus] = await Promise.all([
        api.analytics(),
        api.health(),
      ]);
      setStats(analytics);
      setHealth(healthStatus);
      setLastUpdated(new Date());
    } catch {
      setHealth({ status: "degraded", database: "unreachable" });
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const [title, subtitle] = VIEW_TITLES[activeView];

  return (
    <>
      <header className="page-header">
        <div><p className="eyebrow">CUSTOMER EXPERIENCE PLATFORM</p><h1>{title}</h1><span>{subtitle}</span></div>
        <div className="live-status"><i className={health.status === "healthy" ? "healthy" : "degraded"} /><div><strong>{health.status === "healthy" ? "All systems operational" : "Platform needs attention"}</strong><small>{lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString()}` : "Connecting to API…"}</small></div></div>
      </header>

      {activeView === "overview" && <Overview stats={stats} health={health} onNavigate={onNavigate} />}
      {activeView === "assistant" && <ChatPanel onConversation={refresh} />}
      {activeView === "knowledge" && <KnowledgeCenter />}
      {activeView === "automation" && <ProcessAnalyzer />}
      {activeView === "handoffs" && <HandoffQueue />}
    </>
  );
}

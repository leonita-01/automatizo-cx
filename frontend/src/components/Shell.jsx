import {
  Activity,
  Bot,
  BookOpen,
  Gauge,
  Headphones,
  ShieldCheck,
  Sparkles,
} from "lucide-react";


const NAVIGATION = [
  { id: "overview", label: "Overview", icon: Gauge },
  { id: "assistant", label: "AI Assistant", icon: Bot },
  { id: "knowledge", label: "Knowledge", icon: BookOpen },
  { id: "automation", label: "Automation", icon: Activity },
  { id: "handoffs", label: "Handoffs", icon: Headphones },
];


export default function Shell({
  activeView,
  onNavigate,
  children,
}) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">
            <Sparkles size={20} />
          </span>
          <span>
            Automatizo<strong>CX</strong>
          </span>
        </div>

        <p className="sidebar-label">OPERATE &amp; ASSIST</p>

        <nav>
          {NAVIGATION.map(({ id, label, icon: Icon }) => (
            <button
              className={activeView === id ? "active" : ""}
              key={id}
              onClick={() => onNavigate(id)}
            >
              <Icon size={18} />
              {label}
            </button>
          ))}
        </nav>

        <div className="trust-card">
          <ShieldCheck size={21} />
          <div>
            <strong>Privacy by design</strong>
            <small>PII redaction &amp; audit logging</small>
          </div>
        </div>

        <div className="profile">
          <span>LB</span>
          <div>
            <strong>Leonita Bahtiri</strong>
            <small>Solution Engineering Portfolio</small>
          </div>
        </div>
      </aside>

      <main>{children}</main>
    </div>
  );
}

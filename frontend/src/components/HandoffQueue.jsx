import { useState } from "react";
import { Clock3, Headphones, RefreshCw, ShieldCheck } from "lucide-react";

import { api } from "../services/api";


export default function HandoffQueue() {
  const [adminKey, setAdminKey] = useState(() => sessionStorage.getItem("cx-admin-key") || "");
  const [tickets, setTickets] = useState([]);
  const [events, setEvents] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadOperations() {
    setLoading(true);
    setError("");
    sessionStorage.setItem("cx-admin-key", adminKey);
    try {
      const [handoffs, auditEvents] = await Promise.all([
        api.listHandoffs(adminKey),
        api.listAuditEvents(adminKey),
      ]);
      setTickets(handoffs);
      setEvents(auditEvents);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="operations-grid">
      <section className="panel queue-panel">
        <div className="panel-heading">
          <div><span className="heading-icon"><Headphones size={20} /></span><div><h2>Human Handoff Queue</h2><p>Persisted escalations and integration delivery state</p></div></div>
          <button className="secondary-button" onClick={loadOperations} disabled={loading}><RefreshCw size={15} /> {loading ? "Loading…" : "Refresh"}</button>
        </div>
        <div className="secure-toolbar"><input type="password" value={adminKey} onChange={(event) => setAdminKey(event.target.value)} placeholder="Enter X-Admin-Key" /><small>Protected operational endpoint</small></div>
        {error && <div className="inline-error">{error}</div>}
        <div className="ticket-list">
          {tickets.length === 0 ? <div className="empty-state compact"><Headphones size={26} /><strong>No queue loaded</strong><p>Enter the administrator key and refresh the queue.</p></div> : tickets.map((ticket) => (
            <article className="ticket" key={ticket.id}>
              <div className="ticket-top"><span className={`priority ${ticket.priority}`}>{ticket.priority}</span><span className="ticket-status">{ticket.status}</span></div>
              <strong>{ticket.reason}</strong>
              <p>Ticket {ticket.id.slice(0, 8)} · {ticket.integration_status.replaceAll("_", " ")}</p>
              <small><Clock3 size={13} /> {new Date(ticket.created_at).toLocaleString()}</small>
            </article>
          ))}
        </div>
      </section>

      <section className="panel audit-panel">
        <div className="panel-heading"><div><span className="heading-icon"><ShieldCheck size={20} /></span><div><h2>Security Audit Trail</h2><p>Immutable-style operational evidence</p></div></div></div>
        <div className="audit-list">
          {events.length === 0 ? <div className="empty-state compact"><ShieldCheck size={26} /><strong>No audit data loaded</strong><p>Audit events appear after governed actions.</p></div> : events.map((event) => (
            <article key={event.id}><span className={`audit-dot ${event.outcome}`} /><div><strong>{event.action.replaceAll(".", " · ")}</strong><p>{event.entity_type} {event.entity_id ? `#${event.entity_id.slice(0, 8)}` : ""}</p><small>{new Date(event.created_at).toLocaleString()}</small></div><span className="audit-outcome">{event.outcome}</span></article>
          ))}
        </div>
      </section>
    </div>
  );
}

import { useState } from "react";
import { Activity, ArrowRight, CheckCircle2, ShieldAlert } from "lucide-react";

import { api } from "../services/api";


export default function ProcessAnalyzer() {
  const [assessment, setAssessment] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setLoading(true);
    setError("");
    try {
      const result = await api.assessProcess({
        name: form.get("name"),
        monthly_volume: Number(form.get("volume")),
        average_handle_minutes: Number(form.get("minutes")),
        rule_based_percentage: Number(form.get("rules")),
        systems_count: Number(form.get("systems")),
        sensitive_data: form.get("sensitive") === "on",
      });
      setAssessment(result);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel analyzer-panel">
      <div className="panel-heading">
        <div>
          <span className="heading-icon"><Activity size={20} /></span>
          <div>
            <h2>Automation Opportunity Assessment</h2>
            <p>Transparent business-value and delivery-risk scoring</p>
          </div>
        </div>
      </div>

      <div className="analyzer-layout">
        <form onSubmit={submit}>
          <label>
            Process name
            <input name="name" defaultValue="Billing address change" required />
          </label>
          <div className="form-grid">
            <label>
              Monthly volume
              <input name="volume" type="number" min="0" defaultValue="1200" required />
            </label>
            <label>
              Average handle time
              <div className="input-unit"><input name="minutes" type="number" min="1" defaultValue="8" required /><span>min</span></div>
            </label>
            <label>
              Rule-based work
              <div className="input-unit"><input name="rules" type="number" min="0" max="100" defaultValue="85" required /><span>%</span></div>
            </label>
            <label>
              Systems involved
              <input name="systems" type="number" min="1" max="20" defaultValue="2" required />
            </label>
          </div>
          <label className="checkbox-row">
            <input name="sensitive" type="checkbox" />
            Process contains sensitive customer data
          </label>
          <button className="primary-button full-button" disabled={loading}>
            {loading ? "Assessing…" : "Assess process"} <ArrowRight size={16} />
          </button>
          {error && <div className="inline-error">{error}</div>}
        </form>

        <div className="assessment-result">
          {!assessment ? (
            <div className="empty-state">
              <Activity size={30} />
              <strong>Ready to assess</strong>
              <p>Complete the process profile to calculate opportunity, capacity and risk.</p>
            </div>
          ) : (
            <>
              <div className="score-ring" style={{ "--score": `${assessment.automation_score * 3.6}deg` }}>
                <span>{assessment.automation_score}</span>
                <small>/ 100</small>
              </div>
              <h3>{assessment.recommendation}</h3>
              <div className="result-kpis">
                <div><strong>{assessment.estimated_hours_saved_monthly}</strong><small>hours saved/month</small></div>
                <div><strong>{assessment.estimated_fte_capacity}</strong><small>FTE capacity</small></div>
                <div><strong>{assessment.risk_level}</strong><small>delivery risk</small></div>
              </div>
              <ul className="rationale-list">
                {assessment.rationale.map((reason) => (
                  <li key={reason}>
                    {assessment.risk_level === "high" ? <ShieldAlert size={14} /> : <CheckCircle2 size={14} />}
                    {reason}
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      </div>
    </section>
  );
}

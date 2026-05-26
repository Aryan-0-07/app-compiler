import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

const TABS = ["Summary", "DB Schema", "API Schema", "UI Schema", "Auth Schema", "Log"];

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("Summary");
  const [evalMetrics, setEvalMetrics] = useState(null);
  const [showEval, setShowEval] = useState(false);

  useEffect(() => {
    axios.get("/eval/results")
      .then(res => setEvalMetrics(res.data.metrics))
      .catch(() => {});
  }, []);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setShowEval(false);
    try {
      const response = await axios.post("http://localhost:8000/generate", {
        prompt: prompt,
      });
      setResult(response.data);
      setActiveTab("Summary");
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="header">
        <h1>App Compiler</h1>
        <p>Natural language → working app configuration</p>
        <button
          className="eval-toggle"
          onClick={() => setShowEval(!showEval)}
        >
          {showEval ? "← Back to Compiler" : "📊 View Eval Dashboard"}
        </button>
      </div>

      {showEval ? (
        <EvalDashboard metrics={evalMetrics} />
      ) : (
        <>
          <div className="input-section">
            <textarea
              className="prompt-input"
              placeholder="Describe your app... e.g. Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={4}
            />
            <button
              className="generate-btn"
              onClick={handleGenerate}
              disabled={loading || !prompt.trim()}
            >
              {loading ? "Generating..." : "Generate App Config"}
            </button>
          </div>

          {loading && (
            <div className="loading">
              <div className="spinner"></div>
              <p>Running pipeline: Intent → Architecture → Schemas → Validation → Runtime...</p>
            </div>
          )}

          {error && <div className="error"><p>Error: {error}</p></div>}

          {result && (
            <div className="result">
              <div className="result-header">
                <h2>{result.app_name}</h2>
                <div className="badges">
                  <span className={`badge ${result.is_valid ? "green" : "red"}`}>
                    {result.is_valid ? "Valid" : "Invalid"}
                  </span>
                  <span className="badge blue">{result.total_issues} Issues</span>
                  <span className="badge gray">{result.repair_attempts} Repairs</span>
                  <span className={`badge ${result.runtime?.success ? "green" : "red"}`}>
                    Runtime {result.runtime?.success ? "✅" : "❌"}
                  </span>
                </div>
              </div>

              <div className="tabs">
                {TABS.map((tab) => (
                  <button
                    key={tab}
                    className={`tab ${activeTab === tab ? "active" : ""}`}
                    onClick={() => setActiveTab(tab)}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              <div className="tab-content">
                {activeTab === "Summary" && (
                  <div className="summary-grid">
                    <div className="summary-card">
                      <h3>DB Tables</h3>
                      {result.bundle.db.tables.map((t) => (
                        <div key={t.name} className="item">
                          <strong>{t.name}</strong>
                          <span>{t.columns.length} cols</span>
                        </div>
                      ))}
                    </div>
                    <div className="summary-card">
                      <h3>API Endpoints</h3>
                      {result.bundle.api.endpoints.map((e) => (
                        <div key={e.name} className="item">
                          <strong className={`method ${e.method}`}>{e.method}</strong>
                          <span>{e.path}</span>
                        </div>
                      ))}
                    </div>
                    <div className="summary-card">
                      <h3>UI Pages</h3>
                      {result.bundle.ui.pages.map((p) => (
                        <div key={p.name} className="item">
                          <strong>{p.name}</strong>
                          <span>{p.path}</span>
                        </div>
                      ))}
                    </div>
                    <div className="summary-card">
                      <h3>Auth Roles</h3>
                      {result.bundle.auth.roles.map((r) => (
                        <div key={r.name} className="item">
                          <strong>{r.name}</strong>
                          <span>{r.permissions.length} perms</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {activeTab === "DB Schema" && (
                  <pre className="json-view">{JSON.stringify(result.bundle.db, null, 2)}</pre>
                )}
                {activeTab === "API Schema" && (
                  <pre className="json-view">{JSON.stringify(result.bundle.api, null, 2)}</pre>
                )}
                {activeTab === "UI Schema" && (
                  <pre className="json-view">{JSON.stringify(result.bundle.ui, null, 2)}</pre>
                )}
                {activeTab === "Auth Schema" && (
                  <pre className="json-view">{JSON.stringify(result.bundle.auth, null, 2)}</pre>
                )}
                {activeTab === "Log" && (
                  <div className="log">
                    {result.pipeline_log.map((line, i) => (
                      <div key={i} className="log-line">
                        <span className="log-num">{i + 1}</span>
                        <span>{line}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function EvalDashboard({ metrics }) {
  if (!metrics || !metrics.summary) {
    return (
      <div className="eval-empty">
        No eval data found. Run <code>python eval/runner.py</code> first.
      </div>
    );
  }

  const {
    summary,
    by_type,
    failures,
    latency,
    repairs,
    cases = []
  } = metrics;

  if (!summary || !cases) {
    return <div className="eval-empty">Loading eval data...</div>;
  }

  return (
    <div className="eval-dashboard">
      <h2 className="eval-title">Evaluation Dashboard</h2>
      <p className="eval-subtitle">20 test cases — 10 real prompts + 10 edge cases</p>

      <div className="eval-grid">
        <div className="eval-card green-card">
          <div className="eval-number">{summary.success_rate}%</div>
          <div className="eval-label">Success Rate</div>
          <div className="eval-sub">{summary.passed}/{summary.total_cases} passed</div>
        </div>
        <div className="eval-card blue-card">
          <div className="eval-number">{summary.runtime_success_rate}%</div>
          <div className="eval-label">Runtime Success</div>
          <div className="eval-sub">Executable output</div>
        </div>
        <div className="eval-card purple-card">
          <div className="eval-number">{latency.average_total}s</div>
          <div className="eval-label">Avg Latency</div>
          <div className="eval-sub">{latency.min_total}s — {latency.max_total}s range</div>
        </div>
        <div className="eval-card amber-card">
          <div className="eval-number">{repairs.average}</div>
          <div className="eval-label">Avg Repairs</div>
          <div className="eval-sub">{repairs.total_repairs} total repairs</div>
        </div>
      </div>

      <div className="eval-row">
        <div className="eval-section">
          <h3>By Type</h3>
          <div className="eval-type-row">
            <div className="type-block">
              <div className="type-label">Real Prompts</div>
              <div className="type-bar-bg">
                <div
                  className="type-bar green-bar"
                  style={{ width: `${by_type.real.success_rate}%` }}
                ></div>
              </div>
              <div className="type-stat">
                {by_type.real.passed}/{by_type.real.total} — {by_type.real.success_rate}%
              </div>
            </div>
            <div className="type-block">
              <div className="type-label">Edge Cases</div>
              <div className="type-bar-bg">
                <div
                  className="type-bar amber-bar"
                  style={{ width: `${by_type.edge.success_rate}%` }}
                ></div>
              </div>
              <div className="type-stat">
                {by_type.edge.passed}/{by_type.edge.total} — {by_type.edge.success_rate}%
              </div>
            </div>
          </div>
        </div>

        <div className="eval-section">
          <h3>Failure Breakdown</h3>
          {Object.keys(failures.by_type).length === 0 ? (
            <div className="no-failures">No failures!</div>
          ) : (
            Object.entries(failures.by_type).map(([type, count]) => (
              <div key={type} className="failure-row">
                <span className="failure-type">{type}</span>
                <span className="failure-count">{count}</span>
              </div>
            ))
          )}
        </div>

        <div className="eval-section">
          <h3>Latency by Stage</h3>
          {Object.entries(latency.by_stage).map(([stage, lat]) => (
            <div key={stage} className="latency-row">
              <span className="latency-stage">{stage}</span>
              <div className="latency-bar-bg">
                <div
                  className="latency-bar"
                  style={{
                    width: `${Math.min((lat / latency.max_total) * 100, 100)}%`
                  }}
                ></div>
              </div>
              <span className="latency-val">{lat}s</span>
            </div>
          ))}
        </div>
      </div>

      <div className="eval-section full-width">
        <h3>All Test Cases</h3>
        <div className="cases-table">
          <div className="cases-header">
            <span>ID</span>
            <span>Type</span>
            <span>Prompt</span>
            <span>Status</span>
            <span>Latency</span>
            <span>Repairs</span>
            <span>Runtime</span>
          </div>
          {cases.map((c) => (
            <div key={c.id} className="cases-row">
              <span className="case-id">{c.id}</span>
              <span className={`case-type ${c.type}`}>{c.type}</span>
              <span className="case-prompt">
                {c.prompt.substring(0, 50)}...
              </span>
              <span className={`case-status ${c.success ? "pass" : "fail"}`}>
                {c.success ? "✅ PASS" : "❌ FAIL"}
              </span>
              <span className="case-lat">{c.stage_latency?.total}s</span>
              <span className="case-repairs">{c.repair_attempts}</span>
              <span className={`case-runtime ${c.runtime_success ? "pass" : "fail"}`}>
                {c.runtime_success ? "✅" : "❌"}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
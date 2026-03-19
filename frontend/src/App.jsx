import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { api } from "./api";

const NAV_ITEMS = [
  "Sales Overview",
  "Lead Scoring",
  "Email Generator",
  "Call Intelligence",
  "Rep Performance",
  "AI Copilot"
];

const REP_NAMES = [
  "AE 1 - Jordan Lee",
  "AE 2 - Alex Patel",
  "AE 3 - Morgan Chen",
  "AE 4 - Taylor Alvarez",
  "AE 5 - Casey Robinson",
  "AE 6 - Riley Brooks"
];

function App() {
  const [activePage, setActivePage] = useState("Sales Overview");
  const [leads, setLeads] = useState([]);
  const [emails, setEmails] = useState([]);
  const [calls, setCalls] = useState([]);
  const [revenue, setRevenue] = useState([]);
  const [apiStatus, setApiStatus] = useState({ ok: false, message: "Checking..." });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function boot() {
      try {
        setLoading(true);
        await api.health();
        setApiStatus({ ok: true, message: "Connected" });
        const [leadsData, emailData, callData, revenueData] = await Promise.all([
          api.getLeads(),
          api.getEmailEngagement(),
          api.getCallTranscripts(),
          api.getRevenueHistory()
        ]);
        setLeads(leadsData);
        setEmails(emailData);
        setCalls(callData);
        setRevenue(revenueData);
      } catch (e) {
        setApiStatus({ ok: false, message: "Disconnected" });
        setError(String(e.message || e));
      } finally {
        setLoading(false);
      }
    }
    boot();
  }, []);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h2>Navigation</h2>
        {NAV_ITEMS.map((item) => (
          <button
            key={item}
            className={`nav-btn ${activePage === item ? "active" : ""}`}
            onClick={() => setActivePage(item)}
          >
            {item}
          </button>
        ))}
        <div className={`status ${apiStatus.ok ? "ok" : "bad"}`}>
          API: {apiStatus.message}
        </div>
      </aside>
      <main className="content">
        <header>
          <h1>AI Sales Acceleration Engine</h1>
          <p>React frontend for all modules and features.</p>
        </header>
        {error && <div className="alert error">{error}</div>}
        {loading && <div className="alert">Loading data...</div>}
        {!loading && activePage === "Sales Overview" && (
          <SalesOverview leads={leads} emails={emails} revenue={revenue} />
        )}
        {!loading && activePage === "Lead Scoring" && <LeadScoring leads={leads} />}
        {!loading && activePage === "Email Generator" && <EmailGenerator leads={leads} />}
        {!loading && activePage === "Call Intelligence" && (
          <CallIntelligence calls={calls} />
        )}
        {!loading && activePage === "Rep Performance" && (
          <RepPerformance leads={leads} emails={emails} calls={calls} />
        )}
        {!loading && activePage === "AI Copilot" && <AICopilot leads={leads} />}
      </main>
    </div>
  );
}

function MetricCard({ label, value, caption }) {
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      <div className="metric-caption">{caption}</div>
    </div>
  );
}

function SalesOverview({ leads, emails, revenue }) {
  const totalLeads = leads.length;
  const qualifiedLeads = leads.filter((l) =>
    ["Qualified", "Demo Scheduled", "Proposal Sent", "Negotiation"].includes(l.status)
  ).length;
  const convertedLeads = leads.filter((l) => Number(l.converted) === 1).length;
  const conversionRate = totalLeads ? ((convertedLeads / totalLeads) * 100).toFixed(1) : "0.0";

  const statusData = groupCount(leads, "status");
  const sourceData = groupCount(leads, "lead_source");
  const revenueData = [...revenue]
    .map((r) => ({ month: r.month, mrr: Number(r.mrr) }))
    .sort((a, b) => (a.month > b.month ? 1 : -1));
  const emailDaily = groupEmailDaily(emails);

  return (
    <>
      <section className="metrics-row">
        <MetricCard label="Total Leads" value={formatNum(totalLeads)} caption="CRM records" />
        <MetricCard label="Qualified Pipeline" value={formatNum(qualifiedLeads)} caption="Qualified to negotiation" />
        <MetricCard label="Closed Won" value={formatNum(convertedLeads)} caption="Historical wins" />
        <MetricCard label="Conversion Rate" value={`${conversionRate}%`} caption="Won / total leads" />
      </section>
      <section className="grid2">
        <ChartCard title="Lead Status Distribution">
          <SimplePie data={statusData} />
        </ChartCard>
        <ChartCard title="Leads by Source">
          <SimpleBar data={sourceData} x="name" y="value" />
        </ChartCard>
      </section>
      <section className="grid2">
        <ChartCard title="Revenue History">
          <SimpleLine data={revenueData} x="month" y="mrr" />
        </ChartCard>
        <ChartCard title="Email Engagement Over Time">
          <MultiLine data={emailDaily} x="date" keys={["opens", "clicks", "replies"]} />
        </ChartCard>
      </section>
    </>
  );
}

function LeadScoring({ leads }) {
  const [topLeads, setTopLeads] = useState([]);
  const [limit, setLimit] = useState(20);
  const [selectedLead, setSelectedLead] = useState("");
  const [leadScore, setLeadScore] = useState(null);
  const [message, setMessage] = useState("");

  async function trainModel() {
    setMessage("Training model...");
    try {
      await api.trainModel();
      setMessage("Model trained successfully.");
    } catch (e) {
      setMessage(e.message);
    }
  }

  async function refreshTop() {
    setMessage("Scoring leads...");
    try {
      const rows = await api.topLeads(limit);
      setTopLeads(rows);
      setMessage("Top leads refreshed.");
    } catch (e) {
      setMessage(e.message);
    }
  }

  async function scoreOne() {
    if (!selectedLead) return;
    try {
      const rows = await api.scoreLead(Number(selectedLead));
      setLeadScore(rows[0] || null);
    } catch (e) {
      setMessage(e.message);
    }
  }

  return (
    <>
      <div className="toolbar">
        <button onClick={trainModel}>Train Model</button>
        <label>
          Top lead count
          <input
            type="number"
            value={limit}
            min={5}
            max={100}
            onChange={(e) => setLimit(Number(e.target.value))}
          />
        </label>
        <button onClick={refreshTop}>Refresh Lead Scores</button>
      </div>
      {message && <div className="alert">{message}</div>}
      <section className="grid2">
        <ChartCard title="Top Leads (AI)">
          <DataTable rows={topLeads} />
        </ChartCard>
        <ChartCard title="Top 10 Conversion Probability">
          <SimpleBar
            data={topLeads.slice(0, 10).map((r) => ({
              name: r.company,
              value: Number(r.conversion_probability)
            }))}
            x="name"
            y="value"
          />
        </ChartCard>
      </section>
      <section className="card">
        <h3>Search & Score Individual Lead</h3>
        <div className="toolbar">
          <select value={selectedLead} onChange={(e) => setSelectedLead(e.target.value)}>
            <option value="">Select a lead</option>
            {leads.map((l) => (
              <option key={l.lead_id} value={l.lead_id}>
                Lead {l.lead_id} - {l.company}
              </option>
            ))}
          </select>
          <button onClick={scoreOne}>Get AI Score</button>
        </div>
        {leadScore && (
          <div className="metrics-row">
            <MetricCard
              label="Conversion Probability"
              value={`${(Number(leadScore.conversion_probability) * 100).toFixed(1)}%`}
              caption="Predicted chance to convert"
            />
            <MetricCard
              label="Priority Rank"
              value={`#${leadScore.priority_rank}`}
              caption="Relative ordering"
            />
          </div>
        )}
      </section>
    </>
  );
}

function EmailGenerator({ leads }) {
  const [leadId, setLeadId] = useState("");
  const [variant, setVariant] = useState("A");
  const [email, setEmail] = useState(null);
  const [ab, setAb] = useState(null);
  const [msg, setMsg] = useState("");

  async function generateOne() {
    if (!leadId) return;
    setMsg("Generating email...");
    try {
      const result = await api.generateEmail(Number(leadId), variant);
      setEmail(result);
      setMsg("Email generated.");
    } catch (e) {
      setMsg(e.message);
    }
  }
  async function generateAB() {
    if (!leadId) return;
    setMsg("Generating A/B variants...");
    try {
      const result = await api.generateAB(Number(leadId));
      setAb(result);
      setMsg("A/B variants ready.");
    } catch (e) {
      setMsg(e.message);
    }
  }

  return (
    <section className="card">
      <h3>Email Personalization</h3>
      <div className="toolbar">
        <select value={leadId} onChange={(e) => setLeadId(e.target.value)}>
          <option value="">Choose a lead</option>
          {leads.map((l) => (
            <option key={l.lead_id} value={l.lead_id}>
              Lead {l.lead_id} - {l.company}
            </option>
          ))}
        </select>
        <select value={variant} onChange={(e) => setVariant(e.target.value)}>
          <option value="A">Variant A</option>
          <option value="B">Variant B</option>
        </select>
        <button onClick={generateOne}>Generate Personalized Email</button>
        <button onClick={generateAB}>Generate A/B Variants</button>
      </div>
      {msg && <div className="alert">{msg}</div>}
      {email && (
        <div className="card inner">
          <h4>Generated Email</h4>
          <p><b>Subject:</b> {email.subject}</p>
          <pre>{email.body}</pre>
        </div>
      )}
      {ab && (
        <div className="grid2">
          <div className="card inner">
            <h4>Variant A</h4>
            <p><b>Subject:</b> {ab.variant_a.subject}</p>
            <pre>{ab.variant_a.body}</pre>
          </div>
          <div className="card inner">
            <h4>Variant B</h4>
            <p><b>Subject:</b> {ab.variant_b.subject}</p>
            <pre>{ab.variant_b.body}</pre>
          </div>
        </div>
      )}
    </section>
  );
}

function CallIntelligence({ calls }) {
  const [limit, setLimit] = useState(50);
  const [report, setReport] = useState(null);
  const [callId, setCallId] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [msg, setMsg] = useState("");

  async function getReport() {
    try {
      setMsg("Generating risk report...");
      const r = await api.riskReport(limit);
      setReport(r);
      setMsg("Risk report loaded.");
    } catch (e) {
      setMsg(e.message);
    }
  }
  async function analyze() {
    if (!callId) return;
    const n = Number(String(callId).replace("CALL-", ""));
    try {
      setMsg("Analyzing call...");
      const r = await api.analyzeCall(n);
      setAnalysis(r);
      setMsg("Call analyzed.");
    } catch (e) {
      setMsg(e.message);
    }
  }

  return (
    <>
      <section className="card">
        <h3>Risk Report</h3>
        <div className="toolbar">
          <label>
            Calls
            <input type="number" value={limit} min={10} max={200} onChange={(e) => setLimit(Number(e.target.value))} />
          </label>
          <button onClick={getReport}>Generate Risk Report</button>
        </div>
        {msg && <div className="alert">{msg}</div>}
        {report && (
          <div className="grid3">
            <MetricCard label="Total Calls" value={report.total_calls_analyzed} caption="Analyzed set size" />
            <MetricCard label="High Risk Calls" value={report.high_risk_calls_count} caption="Needs attention" />
            <MetricCard label="Avg Sentiment Score" value={Number(report.average_sentiment_score).toFixed(2)} caption="-1 to +1 scale" />
          </div>
        )}
      </section>
      <section className="card">
        <h3>Analyze Individual Call</h3>
        <div className="toolbar">
          <select value={callId} onChange={(e) => setCallId(e.target.value)}>
            <option value="">Select call</option>
            {calls.map((c) => (
              <option key={c.call_id} value={c.call_id}>
                {c.call_id} - Lead {c.lead_id}
              </option>
            ))}
          </select>
          <button onClick={analyze}>Analyze Call</button>
        </div>
        {analysis && (
          <div className="card inner">
            <p><b>Sentiment:</b> {analysis.sentiment}</p>
            <p><b>Risk:</b> {analysis.risk_level}</p>
            <p><b>Summary:</b> {analysis.summary}</p>
            <p><b>Objections:</b> {analysis.objections_detected.join(", ")}</p>
            <ul>
              {analysis.recommended_next_steps.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
        )}
      </section>
    </>
  );
}

function RepPerformance({ leads, emails, calls }) {
  const [selected, setSelected] = useState("All reps");

  const data = useMemo(() => {
    const repData = REP_NAMES.map((name, idx) => ({
      rep_id: idx + 1,
      rep_name: name,
      total_leads: 0,
      open_leads: 0,
      won_deals: 0,
      lost_deals: 0,
      pipeline_value_open: 0,
      emails_sent: 0,
      opens: 0,
      replies: 0,
      calls_made: 0
    }));
    const byId = Object.fromEntries(repData.map((r) => [r.rep_id, r]));

    leads.forEach((l) => {
      const repId = (Number(l.lead_id) % REP_NAMES.length) + 1;
      const r = byId[repId];
      r.total_leads += 1;
      if (!["Closed Won", "Closed Lost"].includes(l.status)) {
        r.open_leads += 1;
        r.pipeline_value_open += Number(l.estimated_deal_size || 0);
      }
      if (l.status === "Closed Won") r.won_deals += 1;
      if (l.status === "Closed Lost") r.lost_deals += 1;
    });
    emails.forEach((e) => {
      const repId = (Number(e.lead_id) % REP_NAMES.length) + 1;
      const r = byId[repId];
      r.emails_sent += 1;
      r.opens += Number(e.opened || 0);
      r.replies += Number(e.replied || 0);
    });
    calls.forEach((c) => {
      const repId = (Number(c.lead_id) % REP_NAMES.length) + 1;
      byId[repId].calls_made += 1;
    });
    return repData.map((r) => ({
      ...r,
      win_rate: r.total_leads ? (r.won_deals / r.total_leads) * 100 : 0,
      open_rate: r.emails_sent ? (r.opens / r.emails_sent) * 100 : 0,
      reply_rate: r.emails_sent ? (r.replies / r.emails_sent) * 100 : 0
    }));
  }, [leads, emails, calls]);

  const view = selected === "All reps" ? data : data.filter((r) => r.rep_name === selected);

  return (
    <>
      <div className="toolbar">
        <label>
          Select rep
          <select value={selected} onChange={(e) => setSelected(e.target.value)}>
            <option>All reps</option>
            {REP_NAMES.map((r) => (
              <option key={r}>{r}</option>
            ))}
          </select>
        </label>
      </div>
      <section className="card">
        <h3>Per-Rep Table</h3>
        <DataTable rows={view} />
      </section>
      <section className="grid2">
        <ChartCard title="Win Rate by Rep">
          <SimpleBar data={data.map((r) => ({ name: r.rep_name, value: Number(r.win_rate.toFixed(2)) }))} x="name" y="value" />
        </ChartCard>
        <ChartCard title="Email Open Rate by Rep">
          <SimpleBar data={data.map((r) => ({ name: r.rep_name, value: Number(r.open_rate.toFixed(2)) }))} x="name" y="value" />
        </ChartCard>
      </section>
    </>
  );
}

function AICopilot({ leads }) {
  const [limit, setLimit] = useState(10);
  const [suggestions, setSuggestions] = useState([]);
  const [leadId, setLeadId] = useState("");
  const [days, setDays] = useState(14);
  const [steps, setSteps] = useState(4);
  const [sim, setSim] = useState(null);
  const [msg, setMsg] = useState("");

  async function refreshSuggestions() {
    try {
      setMsg("Loading suggestions...");
      setSuggestions(await api.copilotSuggestions(limit));
      setMsg("Suggestions ready.");
    } catch (e) {
      setMsg(e.message);
    }
  }

  async function runSimulation() {
    if (!leadId) return;
    try {
      setMsg("Running simulation...");
      setSim(await api.simulateFollowup(Number(leadId), days, steps));
      setMsg("Simulation complete.");
    } catch (e) {
      setMsg(e.message);
    }
  }

  return (
    <>
      <section className="card">
        <h3>Daily Suggestions</h3>
        <div className="toolbar">
          <label>
            Suggestions
            <input type="number" value={limit} min={5} max={25} onChange={(e) => setLimit(Number(e.target.value))} />
          </label>
          <button onClick={refreshSuggestions}>Refresh Suggestions</button>
        </div>
        {msg && <div className="alert">{msg}</div>}
        <DataTable rows={suggestions} />
      </section>
      <section className="card">
        <h3>Autonomous Follow-Up Simulation</h3>
        <div className="toolbar">
          <select value={leadId} onChange={(e) => setLeadId(e.target.value)}>
            <option value="">Select lead</option>
            {leads.map((l) => (
              <option key={l.lead_id} value={l.lead_id}>
                Lead {l.lead_id} - {l.company}
              </option>
            ))}
          </select>
          <label>
            Days
            <input type="number" value={days} min={7} max={30} onChange={(e) => setDays(Number(e.target.value))} />
          </label>
          <label>
            Steps
            <input type="number" value={steps} min={2} max={6} onChange={(e) => setSteps(Number(e.target.value))} />
          </label>
          <button onClick={runSimulation}>Run Simulation</button>
        </div>
        {sim && (
          <>
            <div className="metrics-row">
              <MetricCard label="Open Rate" value={`${(sim.projected_overall_open_rate * 100).toFixed(1)}%`} caption="Across sequence" />
              <MetricCard label="Reply Rate" value={`${(sim.projected_overall_reply_rate * 100).toFixed(1)}%`} caption="Across sequence" />
              <MetricCard label="Conversion Lift" value={`+${(sim.projected_conversion_lift * 100).toFixed(1)} pts`} caption="Estimated improvement" />
            </div>
            <DataTable rows={sim.sequence || []} />
          </>
        )}
      </section>
    </>
  );
}

function ChartCard({ title, children }) {
  return (
    <section className="card">
      <h3>{title}</h3>
      {children}
    </section>
  );
}

function SimplePie({ data }) {
  const COLORS = ["#0ea5e9", "#2563eb", "#7c3aed", "#16a34a", "#f59e0b", "#ef4444", "#06b6d4"];
  return (
    <ResponsiveContainer width="100%" height={320}>
      <PieChart>
        <Pie data={data} dataKey="value" nameKey="name" outerRadius={110}>
          {data.map((_, idx) => (
            <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}

function SimpleBar({ data, x, y }) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={x} interval={0} angle={-20} textAnchor="end" height={80} />
        <YAxis />
        <Tooltip />
        <Bar dataKey={y} fill="#1d4ed8" />
      </BarChart>
    </ResponsiveContainer>
  );
}

function SimpleLine({ data, x, y }) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={x} />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey={y} stroke="#2563eb" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}

function MultiLine({ data, x, keys }) {
  const colors = ["#1d4ed8", "#f59e0b", "#16a34a"];
  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={x} />
        <YAxis />
        <Tooltip />
        <Legend />
        {keys.map((k, idx) => (
          <Line key={k} type="monotone" dataKey={k} stroke={colors[idx % colors.length]} strokeWidth={2} />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

function DataTable({ rows }) {
  if (!rows || rows.length === 0) return <div className="empty">No data yet.</div>;
  const cols = Object.keys(rows[0]);
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {cols.map((c) => (
              <th key={c}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, idx) => (
            <tr key={idx}>
              {cols.map((c) => (
                <td key={c}>{String(r[c])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function groupCount(rows, key) {
  const map = {};
  rows.forEach((r) => {
    const k = r[key] ?? "Unknown";
    map[k] = (map[k] || 0) + 1;
  });
  return Object.entries(map).map(([name, value]) => ({ name, value }));
}

function groupEmailDaily(rows) {
  const map = {};
  rows.forEach((r) => {
    const d = String(r.sent_at).slice(0, 10);
    if (!map[d]) map[d] = { date: d, opens: 0, clicks: 0, replies: 0 };
    map[d].opens += Number(r.opened || 0);
    map[d].clicks += Number(r.clicked || 0);
    map[d].replies += Number(r.replied || 0);
  });
  return Object.values(map).sort((a, b) => (a.date > b.date ? 1 : -1));
}

function formatNum(n) {
  return Number(n || 0).toLocaleString();
}

export default App;


import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import type { Lang, Stats } from "../types";
import { fetchStats, statsSocketUrl } from "../api";
import { t } from "../i18n";

const COLORS = ["#4f46e5", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"];
const axisTick = { fill: "var(--text-2)", fontSize: 11 };
const tooltipStyle = {
  background: "var(--surface)",
  border: "1px solid var(--border)",
  borderRadius: "10px",
  color: "var(--text-1)",
};

export default function Dashboard({ lang }: { lang: Lang }) {
  const { qid } = useParams();
  const [stats, setStats] = useState<Stats | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!qid) return;
    fetchStats(qid).then(setStats).catch(() => {});

    const ws = new WebSocket(statsSocketUrl(qid));
    wsRef.current = ws;
    ws.onmessage = (e) => setStats(JSON.parse(e.data));
    const ping = setInterval(() => ws.readyState === 1 && ws.send("ping"), 25000);

    return () => {
      clearInterval(ping);
      ws.close();
    };
  }, [qid]);

  if (!stats) return <p className="loading">{t(lang, "waiting")}</p>;

  const praxis = stats.praxis_means.map((p) => ({
    name: p.label[lang] ?? p.dimension,
    mean: p.mean,
  }));

  const items = stats.items
    .filter((i) => i.type === "likert" && i.mean !== null)
    .map((i) => ({ name: i.label[lang].slice(0, 40) + "...", mean: i.mean }));
  const categoricalCount = stats.categorical.length;

  return (
    <div className="dashboard">
      <div className="dash-head">
        <div>
          <span className="eyebrow">{t(lang, "dashboard")}</span>
          <h1>{stats.title[lang]}</h1>
        </div>
        <Link className="btn" to="/admin">{t(lang, "backAdmin")}</Link>
      </div>

      <div className="kpi-grid">
        <div className="kpi accent">
          <div className="kpi-label">{t(lang, "totalResponses")}</div>
          <div className="kpi-num">{stats.total_responses}</div>
          <div className="live-status"><span className="live-dot" /> live</div>
        </div>
        <div className="kpi">
          <div className="kpi-label">{t(lang, "praxisMeans")}</div>
          <div className="kpi-num">{praxis.length}</div>
        </div>
        <div className="kpi">
          <div className="kpi-label">{t(lang, "itemMeans")}</div>
          <div className="kpi-num">{items.length}</div>
        </div>
        <div className="kpi">
          <div className="kpi-label">{t(lang, "distributions")}</div>
          <div className="kpi-num">{categoricalCount}</div>
        </div>
      </div>

      <section className="chart-section">
        <div className="section-head">
          <h2>{t(lang, "praxisMeans")}</h2>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={praxis} margin={{ bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="name" angle={-20} textAnchor="end" interval={0} height={80} tick={axisTick} />
            <YAxis domain={[1, 7]} tick={axisTick} />
            <Tooltip contentStyle={tooltipStyle} />
            <Bar dataKey="mean" fill="#4f46e5" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </section>

      <section className="chart-section">
        <div className="section-head">
          <h2>{t(lang, "itemMeans")}</h2>
        </div>
        <ResponsiveContainer width="100%" height={Math.max(300, items.length * 36)}>
          <BarChart data={items} layout="vertical" margin={{ left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis type="number" domain={[1, 7]} tick={axisTick} />
            <YAxis type="category" dataKey="name" width={260} tick={axisTick} />
            <Tooltip contentStyle={tooltipStyle} />
            <Bar dataKey="mean" fill="#06b6d4" radius={[0, 6, 6, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </section>

      <section className="chart-section">
        <div className="section-head">
          <h2>{t(lang, "distributions")}</h2>
        </div>
        <div className="pie-grid">
          {stats.categorical.map((c) => {
            const data = Object.entries(c.counts).map(([name, value]) => ({ name, value }));
            return (
              <div className="pie-card" key={c.key}>
                <h3>{c.label[lang]}</h3>
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie data={data} dataKey="value" nameKey="name" outerRadius={70} label>
                      {data.map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Pie>
                    <Legend wrapperStyle={{ color: "var(--text-2)", fontSize: 12 }} />
                    <Tooltip contentStyle={tooltipStyle} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}

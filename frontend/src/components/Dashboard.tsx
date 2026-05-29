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

  if (!stats) return <p>{t(lang, "waiting")}</p>;

  const praxis = stats.praxis_means.map((p) => ({
    name: p.label[lang] ?? p.dimension,
    mean: p.mean,
  }));

  const items = stats.items
    .filter((i) => i.type === "likert" && i.mean !== null)
    .map((i) => ({ name: i.label[lang].slice(0, 40) + "...", mean: i.mean }));

  return (
    <div className="dashboard">
      <div className="dash-head">
        <h1>{stats.title[lang]} - {t(lang, "dashboard")}</h1>
        <Link className="btn" to="/admin">{t(lang, "backAdmin")}</Link>
      </div>

      <div className="kpi">
        <div className="kpi-num">{stats.total_responses}</div>
        <div className="kpi-label">{t(lang, "totalResponses")}</div>
        <span className="live-dot" /> live
      </div>

      <section>
        <h2>{t(lang, "praxisMeans")}</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={praxis} margin={{ bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" angle={-20} textAnchor="end" interval={0} height={80} />
            <YAxis domain={[1, 7]} />
            <Tooltip />
            <Bar dataKey="mean" fill="#4f46e5" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </section>

      <section>
        <h2>{t(lang, "itemMeans")}</h2>
        <ResponsiveContainer width="100%" height={Math.max(300, items.length * 36)}>
          <BarChart data={items} layout="vertical" margin={{ left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" domain={[1, 7]} />
            <YAxis type="category" dataKey="name" width={260} tick={{ fontSize: 11 }} />
            <Tooltip />
            <Bar dataKey="mean" fill="#06b6d4" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </section>

      <section>
        <h2>{t(lang, "distributions")}</h2>
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
                    <Legend />
                    <Tooltip />
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

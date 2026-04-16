import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useBeta } from "../hooks/useApi";

interface Props {
  ticker: string;
}

const COLORS = ["#6366f1", "#10b981", "#f59e0b"];

export default function BetaPanel({ ticker }: Props) {
  const { data: beta, isLoading, isError } = useBeta(ticker);

  if (isLoading) return <div className="card loading-card">Loading beta…</div>;
  if (isError || !beta) {
    return (
      <div className="card">
        <h3>FF3 Beta — {ticker}</h3>
        <p className="empty-state">
          No beta decomposition available. Run the beta computation script.
        </p>
      </div>
    );
  }

  const bars = [
    { name: "Mkt-RF", value: +beta.market_beta.toFixed(3) },
    { name: "SMB", value: +(beta.smb_beta ?? 0).toFixed(3) },
    { name: "HML", value: +(beta.hml_beta ?? 0).toFixed(3) },
  ];

  return (
    <div className="card">
      <div className="beta-header">
        <h3>FF3 Beta — {ticker}</h3>
        <span className="badge">
          R² = {(beta.r_squared * 100).toFixed(1)}%
        </span>
      </div>
      <p className="beta-meta">
        Window: {beta.window} days &middot; Computed:{" "}
        {new Date(beta.computed_at).toLocaleDateString()}
      </p>

      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={bars} layout="vertical" barSize={28}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3a" />
          <XAxis
            type="number"
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            domain={["auto", "auto"]}
          />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fontSize: 13, fill: "#e2e8f0", fontWeight: 600 }}
            width={60}
          />
          <Tooltip
            contentStyle={{
              background: "#1e1e2e",
              border: "1px solid #333",
              borderRadius: 8,
              fontSize: 13,
            }}
          />
          <Bar dataKey="value" radius={[0, 6, 6, 0]}>
            {bars.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

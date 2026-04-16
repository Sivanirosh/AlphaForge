import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useVolatility } from "../hooks/useApi";

interface Props {
  ticker: string;
}

export default function VolatilityChart({ ticker }: Props) {
  const { data, isLoading } = useVolatility(ticker);

  if (isLoading) return <div className="card loading-card">Loading volatility…</div>;
  if (!data || data.series.length === 0) return null;

  const series = data.series
    .filter((p) => p.rolling_vol !== null)
    .map((p) => ({
      date: p.date,
      vol: +(p.rolling_vol! * 100).toFixed(2),
    }));

  return (
    <div className="card">
      <h3>
        Rolling Volatility ({data.window}d) — {ticker}
      </h3>
      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={series}>
          <defs>
            <linearGradient id="volGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#f59e0b" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3a" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            tickFormatter={(d: string) => d.slice(5)}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            tickFormatter={(v: number) => `${v}%`}
          />
          <Tooltip
            contentStyle={{
              background: "#1e1e2e",
              border: "1px solid #333",
              borderRadius: 8,
              fontSize: 13,
            }}
            formatter={(v) => [v != null ? `${v}%` : '', "Annualised Vol"]}
            />
          <Area
            type="monotone"
            dataKey="vol"
            stroke="#f59e0b"
            strokeWidth={2}
            fill="url(#volGrad)"
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

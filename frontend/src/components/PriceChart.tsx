import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { usePrices } from "../hooks/useApi";

interface Props {
  ticker: string;
}

export default function PriceChart({ ticker }: Props) {
  const { data: prices, isLoading } = usePrices(ticker);

  if (isLoading) return <div className="card loading-card">Loading prices…</div>;
  if (!prices || prices.length === 0) return null;

  const formatted = prices.map((p) => ({
    date: p.date,
    close: +p.close.toFixed(2),
    high: +p.high.toFixed(2),
    low: +p.low.toFixed(2),
  }));

  return (
    <div className="card">
      <h3>Closing Price — {ticker}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={formatted}>
          <defs>
            <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#6366f1" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#6366f1" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3a" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            tickFormatter={(d: string) => d.slice(5)}
          />
          <YAxis
            domain={["auto", "auto"]}
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            tickFormatter={(v: number) => `$${v}`}
          />
          <Tooltip
            contentStyle={{
              background: "#1e1e2e",
              border: "1px solid #333",
              borderRadius: 8,
              fontSize: 13,
            }}
          />
          <Area
            type="monotone"
            dataKey="close"
            stroke="#6366f1"
            strokeWidth={2}
            fill="url(#priceGrad)"
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

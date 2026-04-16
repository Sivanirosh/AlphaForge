import { useMetrics } from "../hooks/useApi";

interface Props {
  ticker: string;
}

export default function MetricsTable({ ticker }: Props) {
  const { data: metrics, isLoading } = useMetrics(ticker);

  if (isLoading) return <div className="card loading-card">Loading metrics…</div>;
  if (!metrics || metrics.length === 0) {
    return (
      <div className="card">
        <h3>Recent Metrics — {ticker}</h3>
        <p className="empty-state">No metrics computed yet.</p>
      </div>
    );
  }

  const recent = metrics.slice(0, 20);

  return (
    <div className="card">
      <h3>Recent Metrics — {ticker}</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Log Return</th>
              <th>Rolling Vol</th>
              <th>Sharpe</th>
            </tr>
          </thead>
          <tbody>
            {recent.map((m) => (
              <tr key={m.date}>
                <td>{m.date}</td>
                <td className={cellClass(m.log_return)}>
                  {fmt(m.log_return, 4)}
                </td>
                <td>{fmt(m.rolling_vol, 4)}</td>
                <td className={cellClass(m.sharpe_ratio)}>
                  {fmt(m.sharpe_ratio, 2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function fmt(v: number | null, digits: number): string {
  return v !== null && v !== undefined ? v.toFixed(digits) : "—";
}

function cellClass(v: number | null): string {
  if (v === null || v === undefined) return "";
  return v >= 0 ? "positive" : "negative";
}

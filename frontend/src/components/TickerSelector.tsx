import { useTickers } from "../hooks/useApi";

interface Props {
  selected: string | null;
  onSelect: (ticker: string) => void;
}

export default function TickerSelector({ selected, onSelect }: Props) {
  const { data: tickers, isLoading } = useTickers();

  if (isLoading) {
    return <div className="ticker-selector">Loading tickers…</div>;
  }

  if (!tickers || tickers.length === 0) {
    return (
      <div className="ticker-selector">
        <span className="ticker-empty">No tickers available — run ingestion first</span>
      </div>
    );
  }

  return (
    <div className="ticker-selector">
      {tickers.map((t) => (
        <button
          key={t}
          className={`ticker-chip ${selected === t ? "active" : ""}`}
          onClick={() => onSelect(t)}
        >
          {t}
        </button>
      ))}
    </div>
  );
}

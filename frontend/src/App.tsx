import { useState } from "react";
import BetaPanel from "./components/BetaPanel";
import Layout from "./components/Layout";
import MetricsTable from "./components/MetricsTable";
import PriceChart from "./components/PriceChart";
import TickerSelector from "./components/TickerSelector";
import VolatilityChart from "./components/VolatilityChart";

export default function App() {
  const [ticker, setTicker] = useState<string | null>(null);

  return (
    <Layout>
      <TickerSelector selected={ticker} onSelect={setTicker} />

      {ticker ? (
        <div className="dashboard">
          <div className="row-full">
            <PriceChart ticker={ticker} />
          </div>
          <div className="row-half">
            <VolatilityChart ticker={ticker} />
            <BetaPanel ticker={ticker} />
          </div>
          <div className="row-full">
            <MetricsTable ticker={ticker} />
          </div>
        </div>
      ) : (
        <div className="placeholder">
          <p>Select a ticker above to view its dashboard.</p>
        </div>
      )}
    </Layout>
  );
}

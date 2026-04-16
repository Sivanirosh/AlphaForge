import type { ReactNode } from "react";

interface Props {
  children: ReactNode;
}

export default function Layout({ children }: Props) {
  return (
    <div className="layout">
      <header className="header">
        <div className="header-inner">
          <h1 className="logo">
            <span className="logo-alpha">Alpha</span>Forge
          </h1>
          <span className="subtitle">
            Equity Metrics Pipeline
          </span>
        </div>
      </header>
      <main className="main">{children}</main>
    </div>
  );
}

"""Centralised application settings read from environment / .env file."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://alpha:alpha@localhost:5432/alphaforge"
    alpaca_api_key: str = ""
    alpaca_secret_key: str = ""
    tickers: str = "AAPL,MSFT,GOOGL,AMZN,META"
    rolling_window: int = 60

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def ticker_list(self) -> list[str]:
        """Return tickers as a list of uppercase strings."""
        return [t.strip().upper() for t in self.tickers.split(",") if t.strip()]


settings = Settings()

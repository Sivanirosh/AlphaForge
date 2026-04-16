import { useQuery } from "@tanstack/react-query";
import client from "../api/client";
import type {
  BetaDecomposition,
  Metric,
  Price,
  TickerListResponse,
  VolatilityResponse,
} from "../types";

export function useTickers() {
  return useQuery<string[]>({
    queryKey: ["tickers"],
    queryFn: async () => {
      const { data } = await client.get<TickerListResponse>("/tickers");
      return data.tickers;
    },
  });
}

export function usePrices(ticker: string | null) {
  return useQuery<Price[]>({
    queryKey: ["prices", ticker],
    queryFn: async () => {
      const { data } = await client.get<Price[]>(`/prices/${ticker}`);
      return data;
    },
    enabled: !!ticker,
  });
}

export function useMetrics(ticker: string | null) {
  return useQuery<Metric[]>({
    queryKey: ["metrics", ticker],
    queryFn: async () => {
      const { data } = await client.get<Metric[]>(`/metrics/${ticker}`);
      return data;
    },
    enabled: !!ticker,
  });
}

export function useVolatility(ticker: string | null) {
  return useQuery<VolatilityResponse>({
    queryKey: ["volatility", ticker],
    queryFn: async () => {
      const { data } = await client.get<VolatilityResponse>(
        `/metrics/${ticker}/volatility`
      );
      return data;
    },
    enabled: !!ticker,
  });
}

export function useBeta(ticker: string | null) {
  return useQuery<BetaDecomposition>({
    queryKey: ["beta", ticker],
    queryFn: async () => {
      const { data } = await client.get<BetaDecomposition>(
        `/metrics/${ticker}/beta`
      );
      return data;
    },
    enabled: !!ticker,
    retry: false,
  });
}

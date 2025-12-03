import { useState } from "react";

type FetchOptions = {
  method?: string;
  body?: any;
  headers?: Record<string, string>;
};

export function useAuthFetch() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchWithTimeout = async (
    url: string,
    options: FetchOptions = {},
    timeoutMs: 20000
  ) => {
    setLoading(true);
    setError(null);

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });

      clearTimeout(timeout);

      //Handle Failed response
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || data.message || "Request failed");
      }
      return await response.json();
    } catch (err: any) {
      if (err.name === "AbortError") {
        setError("Request Timed Out");
      } else {
        console.log(err.message[0]);
        setError(err.message);
      }
      throw err;
    }finally {
      setLoading(false);
    }
  };
  return { loading, error, fetchWithTimeout };
}
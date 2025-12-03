import { useState } from "react";

type FetchOptions = {
  method?: string;
  body?: any;
  headers?: Record<string, string>;
};

export function useAuthFetch() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Extracts readable message from FastAPI, Django, Node, etc.
  const extractMessage = (data: any): string => {
    if (!data) return "Request failed";

    // FastAPI validation errors: detail = [{ msg: "..."}]
    if (Array.isArray(data.detail) && data.detail.length > 0) {
      return data.detail[0].msg || "Validation error";
    }

    // Normal FastAPI errors
    if (typeof data.detail === "string") return data.detail;

    // Custom APIs
    if (data.message) return data.message;
    if (data.error) return data.error;

    // As fallback
    return JSON.stringify(data);
  };

  const fetchWithTimeout = async (
    url: string,
    options: FetchOptions = {},
    timeoutMs = 20000
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

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const message = extractMessage(data);
        setError(message);
        throw new Error(message);
      }

      return data;
    } catch (err: any) {
      if (err.name === "AbortError") {
        setError("Request Timed Out");
        throw err;
      }

      const message = err.message || "Something went wrong";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, fetchWithTimeout };
}

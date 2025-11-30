import { useState } from "react";

export function useAuth() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Shared function for timeout
  const runWithTimeout = async (callback: () => Promise<any>, timeout = 5000) => {
    setLoading(true);
    setError(null);

    return new Promise(async (resolve, reject) => {
      const timer = setTimeout(() => {
        setLoading(false);
        reject(new Error("Request timed out"));
      }, timeout);

      try {
        const result = await callback();
        clearTimeout(timer);
        setLoading(false);
        resolve(result);
      } catch (err: any) {
        clearTimeout(timer);
        setLoading(false);
        setError(err.message);
        reject(err);
      }
    });
  };

  // Register function
  const registerUser = async (username: string, email: string, password: string) => {
    return runWithTimeout(async () => {
      const res = await fetch("http://localhost:8000/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Registration failed");
      }
      return res.json();
    });
  };

  // Login function
  const loginUser = async (email: string, password: string) => {
    return runWithTimeout(async () => {
      const res = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Invalid email or password");
      }
      return res.json();
    });
  };

  return { loading, error, registerUser, loginUser };
}

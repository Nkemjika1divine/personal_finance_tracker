import { Navigate } from "react-router-dom";
import React from "react";

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem("token");
  const expiry = localStorage.getItem("token_expiry");

  if (!token || !expiry) {
    return <Navigate to="/login" replace />;
  }

  if (Date.now() > Number(expiry)) {
    localStorage.removeItem("token");
    localStorage.removeItem("token_expiry");
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

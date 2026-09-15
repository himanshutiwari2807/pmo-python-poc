import { useQuery } from "@tanstack/react-query";
import "./App.css";
import { API_BASE } from "./lib/queryClient";

async function fetchHealth(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE}/healthz`);
  if (!res.ok) throw new Error(`Backend returned ${res.status}`);
  return res.json();
}

export default function App() {
  const health = useQuery({
    queryKey: ["healthz"],
    queryFn: fetchHealth,
    retry: false,
  });

  return (
    <div className="home">
      <p className="home__eyebrow">PMO Python POC</p>
      <h1 className="home__title">Publisher CMO</h1>
      <p className="home__subtitle">
        FastAPI + React are wired up and talking to each other. This is a
        placeholder home page — the upload and analysis workflow will go
        here next.
      </p>

      <div className="home__status">
        <span className="home__status-dot" />
        {health.isLoading && "Checking backend..."}
        {health.isError && "Backend unreachable"}
        {health.data && `Backend: ${health.data.status}`}
      </div>
    </div>
  );
}

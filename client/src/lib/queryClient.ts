import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient();

export const API_BASE = "http://localhost:8000";

export interface Job {
  id: string;
  input_text: string;
  status: string;
  progress: number;
  result: string | null;
  created_at: string;
}

export async function createJob(inputText: string): Promise<Job> {
  const res = await fetch(`${API_BASE}/api/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input_text: inputText }),
  });
  if (!res.ok) throw new Error(`Failed to create job: ${res.status}`);
  return res.json();
}

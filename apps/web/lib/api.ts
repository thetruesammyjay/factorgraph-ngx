import type { DatasetQuality, PilotExperiment } from "@/types/research";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export async function getApiHealth() {
  const response = await fetch(`${API_URL}/health`, { cache: "no-store" });
  if (!response.ok) throw new Error("Research API is unavailable");
  return response.json() as Promise<{ status: string; service: string; version: string }>;
}

export async function getLatestDatasetQuality(): Promise<DatasetQuality> {
  const response = await fetch(`${API_URL}/datasets/quality/latest`, { cache: "no-store" });
  if (!response.ok) throw new Error("Dataset quality report is unavailable");
  return response.json() as Promise<DatasetQuality>;
}

export async function getLatestPilotExperiment(): Promise<PilotExperiment> {
  const response = await fetch(`${API_URL}/experiments/pilot/latest`, { cache: "no-store" });
  if (!response.ok) throw new Error("Pilot experiment report is unavailable");
  return response.json() as Promise<PilotExperiment>;
}

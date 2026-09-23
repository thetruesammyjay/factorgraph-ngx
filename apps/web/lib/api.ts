import type { DatasetQuality, ExperimentCreatePayload, ExperimentNodeRun, ExperimentRecord, ExperimentRun, FundamentalsCompletion, PilotExperiment } from "@/types/research";

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

export async function getLatestFundamentalsCompletion(): Promise<FundamentalsCompletion> {
  const response = await fetch(`${API_URL}/datasets/fundamentals/completion/latest`, { cache: "no-store" });
  if (!response.ok) throw new Error("Fundamentals completion report is unavailable");
  return response.json() as Promise<FundamentalsCompletion>;
}

export async function createExperiment(payload: ExperimentCreatePayload): Promise<ExperimentRecord> {
  const response = await fetch(`${API_URL}/experiments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("Experiment could not be created");
  return response.json() as Promise<ExperimentRecord>;
}

export async function runExperiment(experimentId: string): Promise<ExperimentRun> {
  const response = await fetch(`${API_URL}/experiments/${experimentId}/run`, { method: "POST" });
  if (!response.ok) throw new Error("Experiment graph could not be executed");
  return response.json() as Promise<ExperimentRun>;
}

export async function getExperimentNodeRun(experimentId: string, nodeName: string): Promise<ExperimentNodeRun> {
  const response = await fetch(`${API_URL}/experiments/${experimentId}/run/nodes/${encodeURIComponent(nodeName)}`, { cache: "no-store" });
  if (!response.ok) throw new Error("Graph node output is unavailable");
  return response.json() as Promise<ExperimentNodeRun>;
}

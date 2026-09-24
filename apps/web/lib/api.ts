import type { DatasetQuality, ExperimentCreatePayload, ExperimentExport, ExperimentList, ExperimentManifest, ExperimentNodeRun, ExperimentPlan, ExperimentRecord, ExperimentRun, FundamentalsCompletion, PilotExperiment } from "@/types/research";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

async function fetchResearchJson<T>(path: string, unavailableMessage: string): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 15_000);
  try {
    const response = await fetch(`${API_URL}${path}`, {
      cache: "no-store",
      signal: controller.signal,
    });
    if (!response.ok) throw new Error(`${unavailableMessage} (HTTP ${response.status})`);
    return await response.json() as T;
  } catch (error) {
    if (controller.signal.aborted) {
      throw new Error("The research API did not respond within 15 seconds.");
    }
    if (error instanceof Error) throw error;
    throw new Error(unavailableMessage);
  } finally {
    window.clearTimeout(timeout);
  }
}

export async function getApiHealth() {
  const response = await fetch(`${API_URL}/health`, { cache: "no-store" });
  if (!response.ok) throw new Error("Research API is unavailable");
  return response.json() as Promise<{ status: string; service: string; version: string }>;
}

export async function getLatestDatasetQuality(): Promise<DatasetQuality> {
  return fetchResearchJson<DatasetQuality>("/datasets/quality/latest", "Dataset quality report is unavailable");
}

export async function getLatestPilotExperiment(): Promise<PilotExperiment> {
  return fetchResearchJson<PilotExperiment>("/experiments/pilot/latest", "Pilot experiment report is unavailable");
}

export async function getLatestFundamentalsCompletion(): Promise<FundamentalsCompletion> {
  return fetchResearchJson<FundamentalsCompletion>("/datasets/fundamentals/completion/latest", "Fundamentals completion report is unavailable");
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

export async function getExperimentRun(experimentId: string): Promise<ExperimentRun> {
  const response = await fetch(`${API_URL}/experiments/${experimentId}/run`, { cache: "no-store" });
  if (!response.ok) throw new Error("Saved experiment run is unavailable");
  return response.json() as Promise<ExperimentRun>;
}

export async function getExperimentNodeRun(experimentId: string, nodeName: string): Promise<ExperimentNodeRun> {
  const response = await fetch(`${API_URL}/experiments/${experimentId}/run/nodes/${encodeURIComponent(nodeName)}`, { cache: "no-store" });
  if (!response.ok) throw new Error("Graph node output is unavailable");
  return response.json() as Promise<ExperimentNodeRun>;
}

export async function getExperimentPlan(experimentId: string): Promise<ExperimentPlan> {
  const response = await fetch(`${API_URL}/experiments/${experimentId}/plan`, { cache: "no-store" });
  if (!response.ok) throw new Error("Experiment plan is unavailable");
  return response.json() as Promise<ExperimentPlan>;
}

export async function getExperimentManifest(experimentId: string): Promise<ExperimentManifest> {
  const response = await fetch(`${API_URL}/experiments/${experimentId}/manifest`, { cache: "no-store" });
  if (!response.ok) throw new Error("Experiment manifest is unavailable");
  return response.json() as Promise<ExperimentManifest>;
}

export async function getExperimentExport(experimentId: string): Promise<ExperimentExport> {
  const response = await fetch(`${API_URL}/experiments/${experimentId}/export`, { cache: "no-store" });
  if (!response.ok) throw new Error("Experiment audit bundle is unavailable");
  return response.json() as Promise<ExperimentExport>;
}

export async function listExperiments(): Promise<ExperimentList> {
  const response = await fetch(`${API_URL}/experiments`, { cache: "no-store" });
  if (!response.ok) throw new Error("Experiment registry is unavailable");
  return response.json() as Promise<ExperimentList>;
}

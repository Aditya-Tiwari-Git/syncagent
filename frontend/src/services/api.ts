import type { AnalyzeRequest, AnalyzeResponse } from '../types/api'

const API_URL = import.meta.env.VITE_BACKEND_URL ?? 'http://localhost:8000'

async function parseError(response: Response): Promise<never> {
  let message = 'The SyncAgent service could not complete the request.'
  try {
    const payload = await response.json()
    if (typeof payload.detail?.error === 'string') message = payload.detail.error
    else if (typeof payload.detail === 'string') message = payload.detail
  } catch {
    // Keep a human-readable fallback when the server response is not JSON.
  }
  throw new Error(message)
}

export async function analyzeScene(request: AnalyzeRequest): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_URL}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })
  if (!response.ok) await parseError(response)
  return response.json() as Promise<AnalyzeResponse>
}

export async function downloadReport(request: AnalyzeRequest): Promise<Blob> {
  const response = await fetch(`${API_URL}/api/report`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })
  if (!response.ok) await parseError(response)
  return response.blob()
}

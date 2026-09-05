export interface AnalyzeRequest {
  scene_description: string
  budget: number
  territory: string
  top_k: number
}

export interface SceneAnalysis {
  mood: string[]
  energy: number
  bpm_min: number
  bpm_max: number
  genres: string[]
  instrumentation: string[]
  pacing: string
  scene_duration_seconds: number
}

export interface TrackRecommendation {
  track_id: string
  title: string
  artist?: string | null
  match_score: number
  license_cost?: number | null
  reason: string
  pre_clearance_status: string
}

export interface RejectedTrack {
  track_id: string
  title: string
  reason: string
  match_score?: number | null
}

export interface AnalyzeResponse {
  success: boolean
  scene_analysis: SceneAnalysis
  recommendations: TrackRecommendation[]
  rejected_candidates: RejectedTrack[]
  total_candidates: number
  disclaimer: string
}

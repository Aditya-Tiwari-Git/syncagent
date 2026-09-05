import { useState } from 'react'
import { ArrowUpRight, Check, ChevronDown, Download, Film, LoaderCircle, ShieldCheck, Sparkles, X } from 'lucide-react'
import { analyzeScene, downloadReport } from './services/api'
import type { AnalyzeRequest, AnalyzeResponse, RejectedTrack, TrackRecommendation } from './types/api'

const defaultScene = 'An exhausted detective walks through an empty Mumbai street at 2 AM after failing to solve a case. It is raining and he feels isolated, exhausted, and hopeless.'
const territories = ['Worldwide', 'US', 'Canada', 'UK', 'Europe', 'India', 'Australia', 'Asia-Pacific']

function scoreClass(score: number) {
  if (score >= 90) return 'score score-high'
  if (score >= 75) return 'score score-mid'
  return 'score score-low'
}

function App() {
  const [scene, setScene] = useState(defaultScene)
  const [budget, setBudget] = useState('800')
  const [territory, setTerritory] = useState('Worldwide')
  const [topK, setTopK] = useState('5')
  const [result, setResult] = useState<AnalyzeResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [reportLoading, setReportLoading] = useState(false)
  const [error, setError] = useState('')

  const request = (): AnalyzeRequest => ({
    scene_description: scene.trim(),
    budget: Number(budget),
    territory,
    top_k: Number(topK),
  })

  async function handleAnalyze() {
    setError('')
    if (scene.trim().length < 20) return setError('Describe the scene in at least 20 characters.')
    if (!Number.isFinite(Number(budget)) || Number(budget) < 0) return setError('Enter a valid non-negative budget.')
    setLoading(true)
    try {
      setResult(await analyzeScene(request()))
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  async function handleReport() {
    setError('')
    setReportLoading(true)
    try {
      const blob = await downloadReport(request())
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'syncagent-pre-clearance-report.pdf'
      link.click()
      URL.revokeObjectURL(url)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Report generation failed.')
    } finally {
      setReportLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="SyncAgent home">
          <span className="brand-mark"><Sparkles size={16} /></span>
          <span>SYNC<span>AGENT</span></span>
        </a>
        <nav aria-label="Primary navigation">
          <a href="#analyze">Analyze</a>
          <a href="#results">Results</a>
          <a href="#about">About</a>
        </nav>
        <div className="status-pill"><span /> Vertex workflow online</div>
      </header>

      <main id="top">
        <section className="hero section-wrap">
          <div className="hero-copy">
            <p className="eyebrow"><Film size={15} /> For filmmakers in post</p>
            <h1>Find the sound<br /><em>before</em> the deadline.</h1>
            <p className="hero-text">AI music pre-clearance for scenes that need the right emotional register and the right licensing path.</p>
            <a className="text-link" href="#analyze">Start an analysis <ArrowUpRight size={16} /></a>
          </div>
          <div className="hero-art" aria-hidden="true">
            <div className="art-grid" />
            <div className="art-orbit orbit-one" /><div className="art-orbit orbit-two" />
            <div className="art-caption"><span>SCENE / 01</span><strong>Atmosphere<br />is a decision.</strong></div>
          </div>
        </section>

        <section className="workspace section-wrap" id="analyze">
          <div className="section-heading"><div><p className="eyebrow">01 / Scene brief</p><h2>What are we scoring?</h2></div><span className="step-note">Input → analysis → clearance</span></div>
          <div className="analysis-grid">
            <div className="form-panel">
              <label htmlFor="scene">Scene description</label>
              <textarea id="scene" value={scene} onChange={(event) => setScene(event.target.value)} placeholder="Describe the emotion, pacing, location, and narrative moment..." />
              <div className="field-meta"><span>Give the agent the cinematic context.</span><span>{scene.length} chars</span></div>
              <div className="form-row">
                <div><label htmlFor="budget">Budget <span>(USD)</span></label><div className="input-prefix"><span>$</span><input id="budget" type="number" min="0" value={budget} onChange={(event) => setBudget(event.target.value)} /></div></div>
                <div><label htmlFor="territory">Territory</label><div className="select-wrap"><select id="territory" value={territory} onChange={(event) => setTerritory(event.target.value)}>{territories.map((item) => <option key={item}>{item}</option>)}</select><ChevronDown size={16} /></div></div>
                <div><label htmlFor="topK">Top tracks</label><div className="select-wrap"><select id="topK" value={topK} onChange={(event) => setTopK(event.target.value)}>{[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((item) => <option key={item}>{item}</option>)}</select><ChevronDown size={16} /></div></div>
              </div>
              {error && <div className="error-message" role="alert"><X size={16} /> {error}</div>}
              <button className="primary-button" onClick={handleAnalyze} disabled={loading}>{loading ? <><LoaderCircle className="spin" size={18} /> Analyzing scene...</> : <>Analyze scene <ArrowUpRight size={18} /></>}</button>
            </div>
            <div className="promise-panel"><p className="eyebrow">The workflow</p><div className="promise-list"><div><span>01</span><strong>Understand</strong><p>Gemini translates your scene into tempo, mood, energy, and texture.</p></div><div><span>02</span><strong>Search</strong><p>ClickHouse queries the approved catalog across creative dimensions.</p></div><div><span>03</span><strong>Pre-clear</strong><p>Deterministic rules separate creative fit from licensing fit.</p></div></div><div className="privacy-note"><ShieldCheck size={17} /><span>Catalog data is the source of truth.<br />No legal clearance claims.</span></div></div>
          </div>
        </section>

        {loading && <section className="loading-state section-wrap" aria-live="polite"><LoaderCircle className="spin" size={22} /><div><strong>SYNCAGENT IS WORKING</strong><p>Understanding the scene, searching the catalog, checking configured rights.</p></div></section>}
        {result && !loading && <Results result={result} onReport={handleReport} reportLoading={reportLoading} />}
      </main>

      <footer id="about" className="footer section-wrap"><div className="brand"><span className="brand-mark"><Sparkles size={16} /></span><span>SYNC<span>AGENT</span></span></div><p>AI music pre-clearance for filmmakers.</p><small>{result?.disclaimer ?? 'Final licensing must be verified with the relevant rights holder.'}</small></footer>
    </div>
  )
}

function Results({ result, onReport, reportLoading }: { result: AnalyzeResponse; onReport: () => void; reportLoading: boolean }) {
  const analysis = result.scene_analysis
  return <section className="results section-wrap" id="results"><div className="section-heading"><div><p className="eyebrow">02 / Intelligence report</p><h2>Your scene, translated.</h2></div><button className="secondary-button" onClick={onReport} disabled={reportLoading}>{reportLoading ? <><LoaderCircle className="spin" size={16} /> Generating...</> : <><Download size={16} /> Download report</>}</button></div><div className="analysis-card"><div><span className="metric-label">Mood</span><div className="tag-list">{analysis.mood.map((item) => <span className="tag" key={item}>{item}</span>)}</div></div><div><span className="metric-label">Energy</span><strong className="metric-value">{analysis.energy}<small> / 5</small></strong></div><div><span className="metric-label">Tempo</span><strong className="metric-value">{analysis.bpm_min}–{analysis.bpm_max}<small> BPM</small></strong></div><div><span className="metric-label">Pacing</span><strong className="metric-value text-cap">{analysis.pacing}</strong></div><div><span className="metric-label">Genres</span><div className="tag-list">{analysis.genres.map((item) => <span className="tag" key={item}>{item}</span>)}</div></div></div><div className="results-columns"><div className="recommendations"><div className="subheading"><span>Recommended tracks</span><b>{result.recommendations.length} passed</b></div>{result.recommendations.length ? result.recommendations.map((track) => <Recommendation key={track.track_id} track={track} />) : <EmptyState />}</div><div className="rejected"><div className="subheading"><span>Rejected candidates</span><b>{result.rejected_candidates.length} filtered</b></div>{result.rejected_candidates.length ? result.rejected_candidates.map((track) => <Rejected key={track.track_id} track={track} />) : <p className="muted-copy">No candidates were rejected by the configured checks.</p>}</div></div><p className="disclaimer"><ShieldCheck size={16} /> {result.disclaimer}</p></section>
}

function Recommendation({ track }: { track: TrackRecommendation }) { return <article className="track-card"><div className="track-head"><div><span className="track-id">{track.track_id}</span><h3>{track.title}</h3><p>{track.artist || 'Catalog artist'}</p></div><div className={scoreClass(track.match_score)}><strong>{Math.round(track.match_score)}%</strong><span>match</span></div></div><div className="track-details"><span><Check size={14} /> Passed checks</span><span>{track.license_cost == null ? 'Price unavailable' : `$${track.license_cost.toLocaleString()} license`}</span></div><p className="track-reason">{track.reason}</p><span className="passed-label">The catalog indicates that this candidate passes the configured pre-clearance checks.</span></article> }
function Rejected({ track }: { track: RejectedTrack }) { return <article className="rejected-card"><div className="rejected-top"><div><span className="track-id">{track.track_id}</span><h3>{track.title}</h3></div><span className="reject-label"><X size={13} /> Rejected</span></div><p>{track.reason}</p>{track.match_score != null && <span className="rejected-score">{Math.round(track.match_score)}% creative match</span>}</article> }
function EmptyState() { return <div className="empty-state"><Sparkles size={22} /><h3>No suitable pre-clearance match</h3><p>No catalog track satisfies all configured creative and licensing constraints. Consider increasing the budget, relaxing territory, or commissioning original music.</p></div> }

export default App

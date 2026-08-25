# SyncAgent Quick Start Guide

Get up and running with SyncAgent in 5 minutes!

## ⚡ 30-Second Setup

```bash
# 1. Clone and navigate
git clone <repo-url>
cd syncagent

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your GCP and ClickHouse credentials

# 5. Run validation
python validate_production.py
```

## 🎬 Quick Examples

### Example 1: Basic Usage

```python
from backend import run_syncagent_pipeline

# Describe your scene
scene = """
A detective walks through rain-soaked Mumbai streets at midnight.
He's exhausted, defeated, and carrying the weight of a case he couldn't solve.
The mood is dark and introspective.
"""

# Run the pipeline
result = run_syncagent_pipeline(
    scene=scene,
    budget=1000.0,
    territory="worldwide"
)

# Get top recommendation
top_track = result['recommendations'][0]
print(f"✓ {top_track.track.title} by {top_track.track.artist}")
print(f"  Score: {top_track.final_score}/100")
print(f"  Price: ${top_track.track.license_price}")
```

### Example 2: Step-by-Step Analysis

```python
from backend.services import (
    analyze_scene,
    search_candidate_tracks,
    validate_track,
    calculate_creative_score,
    calculate_final_score,
)

# Step 1: Analyze scene
scene = "A dramatic action sequence with fast cuts and intense emotions"
requirements = analyze_scene(scene)
print(f"Requirements: {requirements.energy}/5 energy, {requirements.pacing} pacing")

# Step 2: Find candidates
candidates = search_candidate_tracks(requirements, limit=50)
print(f"Found {len(candidates)} candidate tracks")

# Step 3: Score each track
scores = []
for track in candidates:
    creative_score = calculate_creative_score(track, requirements)
    final_score = calculate_final_score(creative_score, track, budget=1000)
    scores.append((track.title, final_score))

# Show top 5
scores.sort(key=lambda x: x[1], reverse=True)
for title, score in scores[:5]:
    print(f"  {title}: {score}/100")
```

### Example 3: Validate Rights

```python
from backend.models import Track
from backend.services import validate_track

track = Track(
    id="DEMO001",
    title="Cinematic Dream",
    artist="John Composer",
    genre="cinematic",
    mood="melancholic",
    bpm=60,
    energy=2,
    duration_seconds=300,
    instrumentation="strings, piano",
    sync_available=True,
    commercial_use=True,
    territory="worldwide",
    license_price=500.0,
    license_type="standard_sync"
)

# Validate for your needs
validation = validate_track(
    track=track,
    budget=1000,
    territory="worldwide",
    require_commercial_use=True
)

if validation.valid:
    print(f"✓ Track approved: {track.title}")
else:
    print(f"✗ Track rejected: {validation.rejection_reasons}")
```

## 📖 Common Tasks

### Task: Run Smoke Tests

```bash
# Test scene analysis
python -m backend.test_scene_analysis

# Test pipeline
python -m backend.test_pipeline

# Test database
python -m tests.test_database
```

### Task: Analyze Logs

```bash
# Main debug log (all operations)
cat logs/syncagent.log

# Error log only
cat logs/syncagent_errors.log

# Last 20 lines
Get-Content logs/syncagent.log -Tail 20
```

### Task: Test Your Changes

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_services.py::test_validate_track -v

# Run with coverage
python -m pytest tests/ --cov=backend --cov-report=html
```

### Task: Check Configuration

```python
from backend.config import settings, PROJECT_ROOT

print(f"Project root: {PROJECT_ROOT}")
print(f"GCP Project: {settings.GOOGLE_CLOUD_PROJECT}")
print(f"ClickHouse Host: {settings.CLICKHOUSE_HOST}")
print(f"Log location: {PROJECT_ROOT}/logs")

# Validate all required vars
settings.validate()
print("✓ All configuration valid")
```

## 🔧 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'backend'"

**Solution:** Run with `-m` flag instead of direct execution:

```bash
# Wrong:
python backend/test_pipeline.py

# Right:
python -m backend.test_pipeline
```

### Problem: "No module named 'google'"

**Solution:** Install dependencies:

```bash
pip install -r requirements.txt
```

### Problem: ClickHouse connection fails

**Solution:** Check credentials in .env:

```bash
# Verify file exists
cat .env

# Check environment variables are loaded
python -c "import os; print(os.getenv('CLICKHOUSE_HOST'))"
```

### Problem: Gemini API returns invalid JSON

**Solution:** Check scene description:

```python
# Scene too short or empty
scene = "A scene"  # Too vague

# Better: Detailed description
scene = """
Close-up of a woman's face as she realizes the truth.
Her expression shifts from hope to despair.
The lighting is cold and blue.
"""
```

### Problem: Validation tests fail

**Solution:** Run setup script:

```bash
# Install all dependencies fresh
pip install --force-reinstall -r requirements.txt

# Run validation
python validate_production.py
```

## 📊 Understanding Scores

### Creative Score (0-100)

| Score Range | Interpretation  | Recommendation          |
| ----------- | --------------- | ----------------------- |
| 90-100      | Perfect match   | Highly recommended      |
| 80-89       | Excellent match | Recommended             |
| 70-79       | Good match      | Consider this track     |
| 60-69       | Fair match      | Acceptable alternative  |
| Below 60    | Poor match      | Look for better options |

**Score Breakdown:**

- Mood: 40 points (matches your mood requirements)
- BPM: 20 points (matches your tempo range)
- Genre: 15 points (matches your genre list)
- Energy: 15 points (matches your energy level)
- Instrumentation: 10 points (has requested instruments)

### Final Score

Your creative score + budget bonus:

- **+5 points**: If price ≤ 50% of budget (excellent value)
- **+2 points**: If price ≤ 75% of budget (good value)
- **Max**: 100 points

## 🎯 API Quick Reference

### run_syncagent_pipeline

```python
result = run_syncagent_pipeline(
    scene="Scene description",
    budget=1000.0,
    territory="worldwide"
)

# Returns:
# {
#     "requirements": SceneRequirements,
#     "recommendations": [ValidatedTrack, ...],
#     "rejected": [ValidatedTrack, ...]
# }
```

### analyze_scene

```python
requirements = analyze_scene(
    scene_description="Scene text"
)

# Returns: SceneRequirements
# - mood: list[str]
# - energy: int (1-5)
# - bpm_min/max: int
# - genres: list[str]
# - instrumentation: list[str]
# - pacing: str (slow/medium/fast)
# - scene_duration_seconds: int
```

### search_candidate_tracks

```python
tracks = search_candidate_tracks(
    requirements=SceneRequirements(...),
    limit=100
)

# Returns: list[Track]
```

### validate_track

```python
validation = validate_track(
    track=Track(...),
    budget=1000.0,
    territory="worldwide",
    require_commercial_use=True
)

# Returns: ValidatedTrack
# - valid: bool
# - rejection_reasons: list[str]
# - creative_score: float
# - final_score: float
```

### calculate_creative_score

```python
score = calculate_creative_score(
    track=Track(...),
    requirements=SceneRequirements(...)
)

# Returns: float (0-100)
```

### calculate_final_score

```python
score = calculate_final_score(
    creative_score=85.5,
    track=Track(...),
    budget=1000.0
)

# Returns: float (0-100)
```

## 📚 Next Steps

- **Read [README.md](README.md)** for complete documentation
- **Read [ARCHITECTURE.md](ARCHITECTURE.md)** for system design
- **Read [CONTRIBUTING.md](CONTRIBUTING.md)** for development guidelines
- **Review [backend/](backend/)** for implementation details
- **Run tests** with `python -m pytest tests/`

## 🆘 Getting Help

1. **Check logs** in `logs/` directory
2. **Review examples** in this file and README
3. **Search issues** for similar problems
4. **Read docstrings** in the code
5. **Ask in discussions** if still stuck

## ✅ Health Check

```bash
# Run this to verify everything is working:
python validate_production.py

# Expected output:
# ✓✓✓ All Production Tests Passed! ✓✓✓
# Codebase Status: PRODUCTION-READY
```

---

**Welcome to SyncAgent!** 🎵 Your AI-powered music synchronization platform is ready to use.

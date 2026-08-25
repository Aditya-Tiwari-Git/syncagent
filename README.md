# SyncAgent - AI-Powered Music Synchronization Platform

SyncAgent is a production-grade intelligent music synchronization platform that analyzes film scenes and recommends the perfect music tracks from a catalog. It uses Google's Gemini AI to understand scene emotions and matches them with a curated ClickHouse database of licensed music.

## 🎯 Features

- **AI-Powered Scene Analysis**: Uses Gemini 2.5 Flash to analyze film scenes and extract structured musical requirements (mood, energy, BPM, genres, instrumentation, pacing)
- **Intelligent Music Search**: Queries ClickHouse database for candidate tracks matching scene requirements efficiently
- **Comprehensive Rights Validation**: Validates tracks for sync rights, commercial use, budget constraints, and territorial restrictions
- **Creative Scoring Algorithm**: Ranks tracks based on 100-point creative fit system (mood, BPM, genre, energy, instrumentation)
- **Budget-Aware Recommendations**: Combines creative score with budget optimization for final ranking
- **Production-Grade Logging**: Structured logging with rotating file handlers and detailed debug information
- **Full Error Handling**: Comprehensive exception handling and validation throughout the pipeline

## 📋 Table of Contents

1. [Architecture](#architecture)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [API Documentation](#api-documentation)
6. [Scoring System](#scoring-system)
7. [Error Handling](#error-handling)
8. [Logging](#logging)
9. [Development](#development)
10. [Testing](#testing)

## 🏗️ Architecture

```
syncagent/
├── backend/                      # Core application logic
│   ├── __init__.py              # Package exports
│   ├── config.py                # Configuration management with validation
│   ├── logging_config.py        # Logging setup and configuration
│   ├── models/                  # Pydantic data models
│   │   ├── __init__.py
│   │   ├── scene.py             # SceneRequirements model with validation
│   │   └── track.py             # Track, ValidatedTrack, TrackRecommendation models
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── scene_analyzer.py    # Gemini AI scene analysis service
│   │   ├── music_search.py      # ClickHouse track search service
│   │   ├── rights_validator.py  # Rights & budget validation service
│   │   ├── ranking.py           # Creative & final scoring service
│   │   ├── sync_pipeline.py     # Main orchestration pipeline
│   │   ├── recommendations.py   # Recommendation formatting
│   │   ├── normalizer.py        # Data normalization utilities
│   │   └── matching.py          # Advanced matching logic
│   └── test_*.py                # Runnable smoke-test scripts
├── database/                    # Database management
│   ├── schema.sql               # ClickHouse table schema
│   ├── generate.py              # Synthetic catalog generator
│   ├── create_table.py          # Table creation script
│   └── generate_load_catalog.py # Load catalog script
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── test_database.py         # Database connectivity tests
│   ├── test_database.py         # Database connectivity test
│   └── test_matching_engine.py  # Matching-engine tests
├── logs/                        # Application logs (auto-created)
│   ├── syncagent.log            # Main debug log
│   └── syncagent_errors.log     # Error log
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .env                         # Local environment (gitignored)
└── README.md                    # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- Google Cloud Project with Vertex AI API enabled
- ClickHouse Cloud account with connection credentials
- pip package manager

### Step-by-Step Setup

#### 1. Clone and Navigate

```bash
git clone <repository-url>
cd syncagent
```

#### 2. Create Virtual Environment

```bash
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS/Linux
python -m venv .venv
source .venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configure Environment

```bash
# Copy template and edit with your credentials
cp .env.example .env

# Edit .env with your actual credentials:
# - GOOGLE_CLOUD_PROJECT: Your GCP project ID
# - GOOGLE_CLOUD_LOCATION: Region (default: us-central1)
# - CLICKHOUSE_HOST: Your ClickHouse Cloud hostname
# - CLICKHOUSE_USER: ClickHouse username
# - CLICKHOUSE_PASSWORD: ClickHouse password
```

#### 5. Initialize Database

```bash
# Create the tracks table
python -m database.create_table

# Generate and load sample music catalog (150 tracks)
python -m database.generate
```

## ⚙️ Configuration

### Environment Variables

| Variable                | Type   | Required | Default     | Description                                           |
| ----------------------- | ------ | -------- | ----------- | ----------------------------------------------------- |
| `GOOGLE_CLOUD_PROJECT`  | String | Yes      | -           | Google Cloud project ID                               |
| `GOOGLE_CLOUD_LOCATION` | String | No       | us-central1 | Vertex AI region (e.g., us-central1, asia-northeast1) |
| `CLICKHOUSE_HOST`       | String | Yes      | -           | ClickHouse Cloud hostname                             |
| `CLICKHOUSE_USER`       | String | Yes      | -           | ClickHouse username                                   |
| `CLICKHOUSE_PASSWORD`   | String | Yes      | -           | ClickHouse password                                   |

### Configuration Validation

Configuration is automatically validated on startup. Missing required variables will raise a `ValueError` with clear instructions.

```python
from backend.config import settings

# Validate configuration
settings.validate()  # Raises ValueError if any required var is missing

# Access settings
print(settings.GOOGLE_CLOUD_PROJECT)
print(settings.CLICKHOUSE_HOST)
```

## 📖 Usage

### Basic Usage: Run the Pipeline

```python
from backend import run_syncagent_pipeline

scene = """
A detective walks alone through an empty Mumbai street at 2 AM
after failing to solve a murder case. It is raining lightly.
He feels exhausted, isolated and hopeless.
"""

result = run_syncagent_pipeline(
    scene=scene,
    budget=1000.0,  # Maximum budget in USD
    territory="india"  # Target territory
)

# Access recommendations
print(f"Found {len(result['recommendations'])} recommendations:")

for i, track_rec in enumerate(result['recommendations'][:5], 1):
    track = track_rec.track
    print(f"{i}. {track.title} by {track.artist}")
    print(f"   Score: {track_rec.final_score}/100")
    print(f"   BPM: {track.bpm}, Energy: {track.energy}, Genre: {track.genre}")
    print(f"   License: ${track.license_price} ({track.license_type})")
```

### Step-by-Step Pipeline Usage

```python
from backend.services import (
    analyze_scene,
    search_candidate_tracks,
    validate_track,
    calculate_creative_score,
    calculate_final_score,
)

# Step 1: Analyze scene
requirements = analyze_scene(scene_description)
print(f"Scene Requirements: Energy={requirements.energy}, Pacing={requirements.pacing}")

# Step 2: Search for candidates
candidates = search_candidate_tracks(requirements)
print(f"Found {len(candidates)} candidates")

# Step 3: Validate individual track
for track in candidates[:1]:
    validation = validate_track(
        track=track,
        budget=1000,
        territory="worldwide"
    )

    if validation.valid:
        # Step 4: Score the track
        creative_score = calculate_creative_score(track, requirements)
        final_score = calculate_final_score(creative_score, track, 1000)

        print(f"Track: {track.title}")
        print(f"Creative Score: {creative_score}/100")
        print(f"Final Score: {final_score}/100")
    else:
        print(f"Track rejected: {validation.rejection_reasons}")
```

### Direct Service Usage

```python
from backend.models import SceneRequirements, Track
from backend.services import validate_track, calculate_creative_score

# Create a scene requirement object
requirements = SceneRequirements(
    mood=["dark", "melancholic"],
    energy=2,
    bpm_min=60,
    bpm_max=80,
    genres=["cinematic", "ambient"],
    instrumentation=["piano", "strings"],
    pacing="slow",
    scene_duration_seconds=120
)

# Create a track
track = Track(
    id="TRACK001",
    title="Midnight Shadows",
    artist="John Composer",
    genre="cinematic",
    mood="dark",
    bpm=72,
    energy=2,
    duration_seconds=300,
    instrumentation="piano, strings",
    sync_available=True,
    commercial_use=True,
    territory="worldwide",
    license_price=500.0,
    license_type="standard_sync"
)

# Validate
validation = validate_track(track, budget=1000, territory="worldwide")
if validation.valid:
    # Score
    score = calculate_creative_score(track, requirements)
    print(f"Creative score: {score}/100")
```

## 📊 API Documentation

### Pipeline Function

```python
def run_syncagent_pipeline(
    scene: str,
    budget: float,
    territory: str,
) -> Dict[str, Any]
```

**Execute the complete SyncAgent music synchronization pipeline.**

**Parameters:**

- `scene` (str): Text description of the film scene
- `budget` (float): Maximum licensing budget in USD
- `territory` (str): Target territory (e.g., 'worldwide', 'india')

**Returns:**

```python
{
    "requirements": SceneRequirements,  # Extracted musical requirements
    "recommendations": List[ValidatedTrack],  # Valid tracks sorted by score
    "rejected": List[ValidatedTrack],  # Tracks that failed validation
}
```

**Raises:**

- `ValueError`: If inputs are invalid
- `Exception`: If external services (Gemini, ClickHouse) fail

### Service Functions

#### analyze_scene

```python
def analyze_scene(scene_description: str) -> SceneRequirements
```

Analyzes a film scene using Gemini AI to extract music requirements.

#### search_candidate_tracks

```python
def search_candidate_tracks(
    requirements: SceneRequirements,
    limit: int = 100
) -> List[Track]
```

Searches ClickHouse for tracks matching BPM requirements.

#### validate_track

```python
def validate_track(
    track: Track,
    budget: float,
    territory: str,
    require_commercial_use: bool = True,
) -> ValidatedTrack
```

Validates a track against licensing and rights requirements.

#### calculate_creative_score

```python
def calculate_creative_score(
    track: Track,
    requirements: SceneRequirements
) -> float
```

Calculates creative fit score (0-100).

#### calculate_final_score

```python
def calculate_final_score(
    creative_score: float,
    track: Track,
    budget: float
) -> float
```

Calculates final ranking score (0-100) with budget adjustments.

## 🎯 Scoring System

### Creative Score (0-100 points)

| Component       | Points | Criteria                             |
| --------------- | ------ | ------------------------------------ |
| Mood            | 40     | Track mood matches any required mood |
| BPM             | 20     | Track BPM within required range      |
| Genre           | 15     | Track genre in required genres       |
| Energy          | 15     | Based on energy level difference     |
| Instrumentation | 10     | Any instrument matches requirements  |

**Energy Scoring:**

- Exact match (difference = 0): 15 points
- 1 level difference: 10 points
- 2 level difference: 5 points
- 3+ levels difference: 0 points

### Final Score Adjustments

The creative score is adjusted based on budget efficiency:

- **+5 points**: If track price ≤ 50% of budget
- **+2 points**: If track price ≤ 75% of budget
- Maximum final score: 100 points

### Validation Criteria

A track is rejected if:

1. Sync rights are not available
2. Commercial use is not permitted (when required)
3. License price exceeds budget
4. Territory doesn't match (unless worldwide)

## ⚠️ Error Handling

The application includes comprehensive error handling:

```python
from pydantic import ValidationError
from backend import run_syncagent_pipeline

try:
    result = run_syncagent_pipeline(
        scene="A dramatic scene",
        budget=500,
        territory="worldwide"
    )
except ValueError as e:
    print(f"Input validation error: {e}")
except Exception as e:
    print(f"Service error: {e}")
    # Check logs/ directory for details
```

### Common Errors

| Error                                           | Cause                                  | Solution                       |
| ----------------------------------------------- | -------------------------------------- | ------------------------------ |
| `ValueError: Scene description cannot be empty` | Empty scene input                      | Provide non-empty scene text   |
| `ValueError: Budget must be positive`           | Budget ≤ 0                             | Use positive budget value      |
| `ValidationError: pacing must be one of...`     | Invalid pacing value                   | Use: slow, medium, or fast     |
| `json.JSONDecodeError`                          | Gemini returned invalid JSON           | Check scene description, retry |
| Database connection error                       | ClickHouse credentials invalid/missing | Verify .env configuration      |

## 📝 Logging

The application uses structured logging with multiple outputs:

### Log Files

- **`logs/syncagent.log`**: All debug and info messages (rotating, 10MB max)
- **`logs/syncagent_errors.log`**: Errors only (rotating, 10MB max)

### Log Levels

- `DEBUG`: Detailed information for debugging (file only)
- `INFO`: General operational messages (console and file)
- `WARNING`: Warning messages (console and file)
- `ERROR`: Error messages (all handlers)

### Accessing Logs

```python
import logging

logger = logging.getLogger("backend")
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### Log Format

```
2024-08-25 14:32:15,123 - backend.services.scene_analyzer - INFO - [scene_analyzer.py:42] - Analyzing scene: A detective walks alone...
```

## 🔧 Development

### Project Structure Best Practices

- **Models** (`backend/models/`): Pure data models with Pydantic validation
- **Services** (`backend/services/`): Stateless business logic with clear responsibility
- **Config** (`backend/config.py`): Centralized configuration management
- **Tests** (`tests/`): Comprehensive unit and integration tests

### Adding New Services

1. Create a new module in `backend/services/`
2. Add comprehensive docstrings with examples
3. Include logging at key points
4. Add error handling for external calls
5. Export from `backend/services/__init__.py`
6. Add corresponding unit tests

Example:

```python
"""New service description."""

import logging

logger = logging.getLogger(__name__)


def new_function(param: str) -> dict:
    """Function description with details.

    Args:
        param: Parameter description

    Returns:
        Return type and description

    Raises:
        Exception: When/why it's raised
    """
    logger.info(f"Starting operation with {param}")

    try:
        # Implementation
        logger.debug("Operation step completed")
        return {"result": "value"}
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        raise
```

### Code Style

- **Type hints**: Required for all functions and class attributes
- **Docstrings**: All public functions and classes
- **Logging**: Use logger for all informational messages
- **Error handling**: Wrap external calls in try-except
- **Validation**: Use Pydantic models for data validation

## 🧪 Testing

### Run Tests

```bash
# All tests
python -m pytest tests/

# Specific test file
python -m pytest tests/test_matching_engine.py

# With coverage
python -m pytest --cov=backend tests/

# Verbose output
python -m pytest -v tests/
```

### Test Structure

```python
import pytest
from backend.services import validate_track
from backend.models import Track

def test_validate_track_valid():
    """Test track validation with valid input."""
    track = Track(...)  # Valid track
    result = validate_track(track, budget=1000, territory="worldwide")
    assert result.valid is True
    assert len(result.rejection_reasons) == 0

def test_validate_track_budget_exceeded():
    """Test track validation with budget exceeded."""
    track = Track(license_price=2000, ...)
    result = validate_track(track, budget=1000, territory="worldwide")
    assert result.valid is False
    assert "exceeds the budget" in result.rejection_reasons[0]
```

### Smoke Tests

Run individual component tests:

```bash
# Scene analysis
python -m backend.test_scene_analysis

# Full pipeline
python -m backend.test_pipeline

# Search functionality
python -m backend.test_search

# Rights validation
python -m backend.test_rights

# Database connectivity
python -m tests.test_database
```

## 📦 Dependencies

Core dependencies (see requirements.txt for full list):

- `google-genai`: Gemini AI API client
- `pydantic`: Data validation and models
- `clickhouse-connect`: ClickHouse database driver
- `python-dotenv`: Environment variable management

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Create a feature branch from `main`
2. Make changes with comprehensive documentation
3. Add/update tests for your changes
4. Run full test suite before submitting PR
5. Ensure all logs are properly configured

## 📞 Support

- Check logs in `logs/` directory for error details
- Review docstrings for function-specific documentation
- Verify environment configuration in `.env`
- Run smoke tests to isolate issues

---

**Last Updated**: August 25, 2024  
**Version**: 1.0.0 (Production)

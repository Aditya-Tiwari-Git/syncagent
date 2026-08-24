# SyncAgent - AI-Powered Music Synchronization Platform

SyncAgent is an intelligent music synchronization platform that analyzes film scenes and recommends the perfect music tracks from a catalog. It uses Google's Gemini AI to understand scene emotions and matches them with a curated music database.

## 🎯 Features

- **Scene Analysis**: Uses Gemini AI to analyze film scenes and extract musical requirements (mood, energy, BPM, genres, instrumentation, pacing)
- **Music Search**: Queries a ClickHouse database for candidate tracks matching scene requirements
- **Rights Validation**: Validates tracks for sync rights, commercial use, budget, and territory restrictions
- **Creative Scoring**: Ranks tracks based on creative fit (mood, BPM, genre, energy, instrumentation)
- **Final Scoring**: Combines creative score with budget considerations for final recommendations

## 🏗️ Architecture

```
syncagent/
├── backend/                 # Core application logic
│   ├── config.py           # Configuration management
│   ├── models/             # Pydantic data models
│   │   ├── scene.py        # SceneRequirements model
│   │   └── track.py        # Track & ValidatedTrack models
│   ├── services/           # Business logic services
│   │   ├── scene_analyzer.py    # Gemini AI scene analysis
│   │   ├── music_search.py      # ClickHouse track search
│   │   ├── rights_validator.py  # Rights & budget validation
│   │   ├── ranking.py           # Creative & final scoring
│   │   ├── sync_pipeline.py     # Main orchestration pipeline
│   │   ├── normalizer.py        # Data normalization
│   │   └── recommendations.py   # Recommendation formatting
│   └── test_*.py           # Runnable smoke-test scripts
├── database/               # Database management
│   ├── schema.sql          # ClickHouse table schema
│   ├── generate.py         # Synthetic catalog generator
│   ├── create_table.py     # Table creation script
│   └── generate_load_catalog.py  # Load catalog script
├── tests/                  # Test suite
│   └── test_database.py    # Database tests
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
└── .env                    # Local environment (not committed)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud Project with Vertex AI enabled
- ClickHouse Cloud account

### Installation

```bash
# Clone the repository
cd syncagent

# Create virtual environment
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Environment Variables

| Variable                | Description                             | Required |
| ----------------------- | --------------------------------------- | -------- |
| `GOOGLE_CLOUD_PROJECT`  | Google Cloud project ID                 | Yes      |
| `GOOGLE_CLOUD_LOCATION` | Vertex AI region (default: us-central1) | No       |
| `CLICKHOUSE_HOST`       | ClickHouse Cloud host                   | Yes      |
| `CLICKHOUSE_USER`       | ClickHouse username                     | Yes      |
| `CLICKHOUSE_PASSWORD`   | ClickHouse password                     | Yes      |

### Generate Music Catalog

```bash
# Generate and load synthetic music catalog into ClickHouse
python -m database.generate
```

### Run Scene Analysis

```bash
# Test scene analysis with Gemini
python -m backend.test_scene_analysis
```

### Run Full Pipeline

```bash
# Test the complete sync pipeline
python -m backend.test_pipeline
```

## 📖 Usage

### Basic Scene Analysis

```python
from backend.services.scene_analyzer import analyze_scene

scene = """
A detective walks alone through an empty Mumbai street
at 2 AM after failing to solve a murder case.

It is raining lightly.

He feels exhausted, isolated and hopeless.
"""

requirements = analyze_scene(scene)
print(requirements.model_dump_json(indent=2))
```

### Full Sync Pipeline

```python
from backend.services.sync_pipeline import run_syncagent_pipeline

scene = "Your scene description here..."
budget = 500.0
territory = "india"

result = run_syncagent_pipeline(scene, budget, territory)

# Access recommendations
for track in result["recommendations"]:
    print(f"{track.track.title} - {track.track.artist} (Score: {track.final_score})")
```

## 🧪 Testing

```bash
# Run the database connectivity check
python -m tests.test_database

# Run specific test
python -m backend.test_scene_analysis
python -m backend.test_pipeline
python -m backend.test_search
python -m backend.test_rights
```

## 📊 Data Models

### SceneRequirements

```python
class SceneRequirements(BaseModel):
    mood: List[str]           # 1-3 mood words (e.g., ["melancholic", "dark"])
    energy: int               # 1-5 energy level
    bpm_min: int              # Minimum BPM
    bpm_max: int              # Maximum BPM
    genres: List[str]         # 1-3 genres
    instrumentation: List[str] # Instruments
    pacing: str               # "slow", "medium", or "fast"
```

### Track

```python
class Track(BaseModel):
    id: str
    title: str
    artist: str
    genre: str
    mood: str
    bpm: int
    energy: int
    duration_seconds: int
    instrumentation: str
    sync_available: bool
    commercial_use: bool
    territory: str
    license_price: float
    license_type: str
```

## 🔧 Development

### Project Structure

- **Models** (`backend/models/`): Pydantic models for type safety and validation
- **Services** (`backend/services/`): Single-responsibility business logic modules
- **Config** (`backend/config.py`): Centralized configuration via environment variables
- **Database** (`database/`): ClickHouse schema, data generation, and loading scripts

### Adding New Services

1. Create service module in `backend/services/`
2. Add imports to `backend/services/__init__.py`
3. Add focused tests under `tests/` or smoke tests under `backend/`

### Code Style

- Type hints required for all functions
- Pydantic models for data validation
- Docstrings for all public functions
- Run tests before committing

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📞 Support

For issues and questions, please open a GitHub issue.

# SyncAgent Architecture & Design Guide

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    SyncAgent Pipeline                           │
└─────────────────────────────────────────────────────────────────┘
                                ▲
                                │
                ┌───────────────┴───────────────┐
                │                               │
         ┌──────▼──────┐              ┌────────▼─────────┐
         │   Gemini    │              │   ClickHouse    │
         │   (Scene    │              │   (Music        │
         │  Analysis)  │              │   Catalog)      │
         └──────▲──────┘              └────────▲─────────┘
                │                               │
    ┌───────────┴───────────┬───────────────────┴──────────┐
    │                       │                              │
┌───▼─────────────────┐  ┌──▼────────────────────┐  ┌──────▼──────┐
│  Scene Analyzer     │  │  Music Search         │  │ Rights      │
│  Service            │  │  Service              │  │ Validator   │
│                     │  │                       │  │ Service     │
│  Input:             │  │  Input:               │  │             │
│  - Scene text       │  │  - Requirements       │  │ Input:      │
│  - Max tokens       │  │  - Limit              │  │ - Track     │
│                     │  │                       │  │ - Budget    │
│  Output:            │  │  Output:              │  │ - Territory │
│  - Requirements     │  │  - Tracks             │  │             │
│                     │  │  - Scores             │  │ Output:     │
└─────────────────────┘  └───────────────────────┘  │ - Valid:    │
                                                    │   bool      │
                         ┌──────────────────────┐   │ - Reasons   │
                         │  Creative Scoring    │   └─────────────┘
                         │  Service             │
                         │                      │
                         │  Input:              │
                         │  - Track             │
                         │  - Requirements      │
                         │                      │
                         │  Output:             │
                         │  - Creative Score    │
                         │    (0-100)           │
                         │  - Final Score       │
                         │    (0-100)           │
                         └──────────────────────┘
                                  ▲
                                  │
                         ┌────────┴─────────┐
                         │                  │
                ┌────────▼────────┐   ┌─────▼──────┐
                │  SceneRequire   │   │  Track     │
                │  ments Model    │   │  Model     │
                │  (Pydantic)     │   │  (Pydantic)│
                └─────────────────┘   └────────────┘
```

### Component Responsibilities

| Component            | Purpose                      | Dependencies       | Error Handling                   |
| -------------------- | ---------------------------- | ------------------ | -------------------------------- |
| **Scene Analyzer**   | Parse scene with Gemini AI   | google-genai       | Retry on API error, timeout      |
| **Music Search**     | Query ClickHouse catalog     | clickhouse-connect | Reconnect on failure, log errors |
| **Rights Validator** | Check sync/commercial rights | None (data only)   | Log rejections, continue         |
| **Creative Scoring** | Calculate fit score          | None (data only)   | Log at debug level               |
| **Pipeline**         | Orchestrate services         | All above          | Aggregate errors, return status  |

## 📋 Data Flow

### Complete Pipeline Flow

```
INPUT: Scene description, Budget, Territory
  │
  ├─► [Scene Analyzer]
  │   ├─ Validate input (non-empty)
  │   ├─ Send to Gemini with structured prompt
  │   ├─ Parse JSON response
  │   ├─ Validate with Pydantic
  │   └─► OUTPUT: SceneRequirements
  │
  ├─► [Music Search]
  │   ├─ Extract BPM range from requirements
  │   ├─ Query ClickHouse database
  │   ├─ Parse results
  │   └─► OUTPUT: List[Track]
  │
  ├─► [Per Track: Validate Rights]
  │   ├─ Check sync_available
  │   ├─ Check commercial_use (if required)
  │   ├─ Compare price vs budget
  │   ├─ Verify territory
  │   └─► OUTPUT: ValidatedTrack (valid=True|False)
  │
  ├─► [Per Valid Track: Score]
  │   ├─ Calculate creative_score (0-100)
  │   │   ├─ Mood match: 40 points
  │   │   ├─ BPM match: 20 points
  │   │   ├─ Genre match: 15 points
  │   │   ├─ Energy match: 15 points (variable)
  │   │   └─ Instrumentation: 10 points
  │   ├─ Apply budget bonus
  │   ├─ Calculate final_score
  │   └─► OUTPUT: Updated ValidatedTrack with scores
  │
  └─► [Sort & Return]
      └─► OUTPUT: {
              requirements: SceneRequirements,
              recommendations: List[ValidatedTrack] (sorted by final_score desc),
              rejected: List[ValidatedTrack]
          }
```

## 🔄 Service Layer Pattern

### Standard Service Function Structure

All services follow this pattern:

```python
"""Service description."""

import logging
from backend.models import InputModel, OutputModel

logger = logging.getLogger(__name__)


def service_function(input_param: InputModel) -> OutputModel:
    """Clear description of what this does.

    Args:
        input_param: Parameter description with type

    Returns:
        Return type and description

    Raises:
        ValueError: For input validation failures
        Exception: For external service failures
    """
    # Step 1: Log entry
    logger.info(f"Starting operation with input: {input_param}")

    try:
        # Step 2: Validate input
        if not is_valid(input_param):
            raise ValueError("Input validation failed: ...")
        logger.debug("Input validation passed")

        # Step 3: Process
        result = process(input_param)
        logger.debug("Processing complete")

        # Step 4: Log success
        logger.info(f"Operation successful")

        return result

    except ValueError as e:
        # Known validation errors
        logger.error(f"Validation error: {e}")
        raise
    except Exception as e:
        # Unexpected errors (API failures, etc.)
        logger.error(f"Operation failed: {e}", exc_info=True)
        raise
```

### Key Principles

1. **Single Responsibility**: Each service has one clear purpose
2. **Stateless**: Services don't maintain state between calls
3. **Input Validation**: Always validate at service boundary
4. **Comprehensive Logging**: Log at DEBUG (detail), INFO (flow), ERROR (problems)
5. **Explicit Error Handling**: Catch specific errors, log, and re-raise
6. **Type Safety**: Full type hints on all functions
7. **Documentation**: Docstring with Args, Returns, Raises, Examples

## 📊 Data Models

### Model Hierarchy

```
Pydantic BaseModel (validation layer)
    │
    ├─ SceneRequirements (from Gemini analysis)
    │   └─ Validates: mood (1-3), energy (1-5), BPM range, genres, instrumentation, pacing
    │
    ├─ Track (from database)
    │   └─ Represents: catalog entry with all musical properties
    │
    ├─ ValidatedTrack (validation result)
    │   ├─ Wraps: Track
    │   ├─ Adds: valid (bool), rejection_reasons (list), scores
    │   └─ Status: Track passed/failed validation
    │
    └─ TrackRecommendation (final output)
        ├─ Wraps: ValidatedTrack
        ├─ Adds: explanation (why recommended)
        └─ Status: Ready for user presentation
```

### Model Validation Strategy

Each model validates:

**At Creation Time (Pydantic):**

- Field type correctness
- Field value ranges (min/max, gt/lt)
- Field length constraints (strings, lists)
- Custom validators (e.g., BPM range ordering)

**At Service Boundaries:**

- Non-empty inputs (strings, lists)
- Business logic constraints (budget > 0)
- External data format validation

**During Processing:**

- Each service logs validation step
- Errors collected in rejection_reasons
- Processing continues on per-item errors

## 🔑 Key Design Decisions

### 1. Gemini for Scene Analysis

**Why Gemini?**

- Understands natural language context
- Structured JSON output capability
- Fast inference (Flash model)
- Cost-effective

**How?**

- Send scene description + specific prompt
- Expect JSON with required fields
- Validate output matches SceneRequirements schema
- Retry on malformed JSON

### 2. ClickHouse for Music Catalog

**Why ClickHouse?**

- Columnar storage (fast queries on BPM/energy)
- Excellent for analytical queries
- Cloud hosting available
- Good for large catalogs (millions of tracks)

**How?**

- BPM used as primary search filter
- Secondary filters applied in-memory
- Results mapped to Track models
- Connection pooling for scalability

### 3. Scoring Algorithm

**Why 100-point scale?**

- Easy to understand (0-100%)
- Allows granular differentiation
- Scales well with multiple factors

**Component weights:**

- Mood (40%): Most important for emotional fit
- BPM (20%): Critical for pacing
- Genre (15%): Second-order musical match
- Energy (15%): Reinforces mood match
- Instrumentation (10%): Texture preference

**Budget adjustment:**

- Encourages efficient spend
- Rewards price optimization
- Maximum benefit: +5 points

### 4. Error Handling Strategy

**Three-tier approach:**

1. **Input Validation** (ValueError)
   - Caught at service entry
   - Clear error message
   - Example: "Scene cannot be empty"

2. **Processing Errors** (Service-specific)
   - Logged at ERROR level
   - May retry if appropriate
   - Example: Gemini API timeout

3. **Data Errors** (Per-item)
   - Logged at DEBUG level
   - Collected in rejection_reasons
   - Processing continues

## 🔌 Extension Points

### Adding New Scoring Factor

```python
# In backend/services/ranking.py

def calculate_creative_score(track: Track, requirements: SceneRequirements) -> float:
    """Calculate creative score with new factor."""

    score = 0.0

    # Existing factors...
    if track.mood in requirements.mood:
        score += 40.0

    # NEW FACTOR: Lyrical complexity (example)
    if hasattr(track, 'lyrical_complexity'):
        if track.lyrical_complexity <= 2:
            score += 5.0  # 5 points for instrumental/minimal lyrics

    logger.debug(f"Track {track.id}: creative score = {score}")
    return min(score, 100.0)
```

### Adding New Validation Rule

```python
# In backend/services/rights_validator.py

def validate_track(track: Track, budget: float, ...) -> ValidatedTrack:
    """Validate with new rule."""

    rejection_reasons = []

    # Existing checks...
    if not track.sync_available:
        rejection_reasons.append("Sync rights not available")

    # NEW CHECK: Exclusivity constraint
    if hasattr(track, 'is_exclusive') and track.is_exclusive:
        if budget < 5000:  # Expensive for exclusive
            rejection_reasons.append("Exclusive license requires higher budget")

    return ValidatedTrack(
        track=track,
        valid=len(rejection_reasons) == 0,
        rejection_reasons=rejection_reasons,
        creative_score=0.0,
        final_score=0.0
    )
```

### Adding New Service

```python
# In backend/services/new_service.py

def new_operation(input_data: InputType) -> OutputType:
    """New service for X."""

    logger.info(f"Starting operation")

    try:
        result = process(input_data)
        logger.info("Operation complete")
        return result
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        raise

# In backend/services/__init__.py
from backend.services.new_service import new_operation
__all__ = [..., "new_operation"]

# In backend/__init__.py
from backend.services import new_operation
__all__ = [..., "new_operation"]

# In backend/services/sync_pipeline.py
from backend.services import new_operation
# Use in pipeline as needed
```

## 📈 Performance Considerations

### Bottlenecks

1. **Gemini API Call**: ~500-2000ms
   - Solution: Consider caching for similar scenes
   - Future: Batch multiple scenes

2. **ClickHouse Query**: ~50-500ms depending on catalog size
   - Solution: Index on BPM for fast range queries
   - Future: Pre-filter by genre before BPM range

3. **Per-Track Processing**: O(n) where n = number of tracks
   - Solution: Efficient model creation
   - Future: Parallel processing for large catalogs

### Scaling Strategy

1. **In-Memory Caching**

   ```python
   from functools import lru_cache

   @lru_cache(maxsize=100)
   def analyze_scene(scene_description: str) -> SceneRequirements:
       return analyze_scene_impl(scene_description)
   ```

2. **Connection Pooling**
   - ClickHouse client handles pooling
   - Config: max_connections

3. **Batch Processing**
   ```python
   def process_scenes_batch(scenes: list[str]) -> list[dict]:
       results = []
       for scene in scenes:
           results.append(run_syncagent_pipeline(scene, ...))
       return results
   ```

## 🧪 Testing Strategy

### Test Pyramid

```
        ▲
       /│\
      / │ \  E2E Tests (1)
     /  │  \ - Full pipeline
    /   │   \- Requires external APIs
   /────┼────\
  /     │     \ Integration Tests (3)
 /      │      \- Service combinations
/───────┼───────\- Mock external APIs
        │
   ┌─────┴─────┐  Unit Tests (many)
   │   Unit    │  - Individual functions
   │   Tests   │  - No external calls
   └───────────┘  - Fast (~10-100ms each)
```

### Test Categories

1. **Unit Tests** (in `tests/test_services.py`)
   - Test individual functions
   - Mock external dependencies
   - Fast execution

2. **Model Tests** (in `tests/test_models.py`)
   - Test Pydantic validation
   - Test edge cases
   - Test invalid inputs

3. **Integration Tests** (in `tests/test_pipeline.py`)
   - Test service combinations
   - Use real or mocked APIs
   - Require credentials

4. **Smoke Tests** (in `backend/test_*.py`)
   - Quick functionality check
   - Runnable: `python -m backend.test_X`
   - Good for CI/CD

## 📚 Module Responsibilities

| Module                                 | Responsibility           | Tests                                              |
| -------------------------------------- | ------------------------ | -------------------------------------------------- |
| `backend/config.py`                    | Load & validate env vars | test_config_valid, test_config_missing             |
| `backend/models/scene.py`              | Scene requirements model | test_scene_valid, test_scene_validation            |
| `backend/models/track.py`              | Track data models        | test_track_creation, test_validation               |
| `backend/services/scene_analyzer.py`   | Gemini integration       | test_analyze_scene_valid, test_analyze_scene_error |
| `backend/services/music_search.py`     | ClickHouse queries       | test_search_candidates, test_search_empty          |
| `backend/services/rights_validator.py` | Track validation         | test_validate_valid, test_validate_budget          |
| `backend/services/ranking.py`          | Scoring algorithm        | test_creative_score, test_final_score              |
| `backend/services/sync_pipeline.py`    | Main orchestration       | test_pipeline_valid, test_pipeline_error           |

## 🚀 Deployment Considerations

### Environment Setup

- Python 3.11+
- Virtual environment required
- pip for dependency management

### External Dependencies

- Google Cloud credentials (GOOGLE_CLOUD_PROJECT)
- ClickHouse Cloud credentials
- Network access to both services

### Monitoring

- Check `logs/syncagent.log` for INFO level
- Check `logs/syncagent_errors.log` for errors
- Monitor error rates and API latency

### Scaling to Production

1. Add request queuing (Celery/RQ)
2. Add caching layer (Redis)
3. Add rate limiting
4. Add monitoring (Prometheus/DataDog)
5. Add tracing (OpenTelemetry)

---

This architecture is designed for:

- ✅ Maintainability through clear separation of concerns
- ✅ Testability through stateless services and dependency injection
- ✅ Reliability through comprehensive error handling and logging
- ✅ Scalability through modular design and extension points
- ✅ Production readiness through validation and monitoring

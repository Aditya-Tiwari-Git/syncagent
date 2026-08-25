# Contributing to SyncAgent

Thank you for your interest in contributing to SyncAgent! This guide provides standards and practices for maintaining production-grade code quality.

## 📋 Development Standards

### Code Style

All contributions must follow these standards:

**Type Hints** - Required for all functions and class attributes:

```python
def analyze_scene(scene_description: str) -> SceneRequirements:
    """Analyze a film scene."""
```

**Docstrings** - All public functions and classes must have comprehensive docstrings:

```python
def calculate_score(track: Track, requirements: SceneRequirements) -> float:
    """Calculate creative fit score for a track.

    Args:
        track: The music track to evaluate
        requirements: Scene requirements to match against

    Returns:
        Creative fit score (0-100)

    Raises:
        ValueError: If track or requirements are invalid

    Examples:
        >>> track = Track(...)
        >>> requirements = SceneRequirements(...)
        >>> score = calculate_score(track, requirements)
        >>> print(f"Score: {score}/100")
    """
```

**Logging** - All key operations must include logging:

```python
import logging

logger = logging.getLogger(__name__)

def process_data(data: dict) -> dict:
    logger.info(f"Processing data with {len(data)} items")
    try:
        # Process data
        logger.debug("Processing step 1 completed")
        result = transform(data)
        logger.info(f"Processing complete: {len(result)} items")
        return result
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise
```

**Error Handling** - All external calls must be wrapped in try-except:

```python
def external_api_call(param: str) -> dict:
    logger.info(f"Starting API call with {param}")
    try:
        result = external_service.call(param)
        logger.debug(f"API call result: {result}")
        return result
    except Exception as e:
        logger.error(f"API call failed: {e}")
        raise
```

**Validation** - Use Pydantic for data validation:

```python
from pydantic import BaseModel, Field

class MyData(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    value: float = Field(..., gt=0, le=1000)
    tags: list[str] = Field(default_factory=list, min_length=1, max_length=10)
```

## 🔧 Adding New Features

### New Service Function

1. **Create the service file** in `backend/services/`:

```python
"""Service description for documentation."""

import logging
from backend.models import YourModel
from backend.config import settings

logger = logging.getLogger(__name__)


def your_function(param: YourType) -> ReturnType:
    """Clear description of what this does.

    Args:
        param: Parameter description

    Returns:
        Return type and description

    Raises:
        ValueError: When validation fails
        Exception: When external service fails

    Examples:
        >>> result = your_function("test")
        >>> print(result)
    """
    logger.info(f"Starting operation with {param}")

    try:
        # Validate input
        if not param:
            raise ValueError("Parameter cannot be empty")

        # Perform operation
        logger.debug("Step 1: Initialization")
        result = process(param)
        logger.debug("Step 2: Processing")

        logger.info(f"Operation complete")
        return result

    except ValueError as e:
        logger.error(f"Validation failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        raise
```

2. **Export from services/**init**.py**:

```python
from backend.services.your_module import your_function

__all__ = [
    "your_function",
]
```

3. **Export from backend/**init**.py**:

```python
from backend.services import your_function

__all__ = [
    # ... existing exports
    "your_function",
]
```

4. **Add unit tests** in `tests/test_services.py`:

```python
def test_your_function_valid():
    """Test your function with valid input."""
    result = your_function("valid_input")
    assert result is not None
    assert isinstance(result, ExpectedType)

def test_your_function_invalid():
    """Test your function with invalid input."""
    with pytest.raises(ValueError):
        your_function("")
```

### New Data Model

1. **Create model** in `backend/models/your_model.py`:

```python
"""Data model for X."""

from pydantic import BaseModel, Field

class YourModel(BaseModel):
    """Description of what this model represents."""

    field1: str = Field(..., min_length=1, max_length=100)
    field2: int = Field(..., ge=0, le=100)
    field3: list[str] = Field(default_factory=list)
```

2. **Export from models/**init**.py**:

```python
from backend.models.your_model import YourModel

__all__ = [
    "YourModel",
]
```

3. **Add validation tests**:

```python
def test_model_valid():
    model = YourModel(field1="test", field2=50)
    assert model.field1 == "test"

def test_model_validation():
    with pytest.raises(ValueError):
        YourModel(field1="", field2=50)  # field1 too short
```

## 📝 Documentation Requirements

### For New Functions

- Clear description of purpose
- Args section with types and descriptions
- Returns section with type and description
- Raises section with exceptions
- Examples section with usage
- Comments for complex logic

### For New Modules

- Module docstring at the top
- Description of module purpose
- List of main functions/classes
- Import organization

### For Bug Fixes

- Include test case that reproduces the bug
- Document the fix in comments
- Update relevant documentation

## 🧪 Testing Requirements

### Unit Tests

All new code requires unit tests:

```bash
# Run specific test
python -m pytest tests/test_your_feature.py -v

# Run with coverage
python -m pytest tests/ --cov=backend

# Check coverage
python -m pytest tests/ --cov=backend --cov-report=html
```

### Test Organization

```python
import pytest
from backend.services import your_function
from backend.models import YourModel

class TestYourFunction:
    """Test suite for your_function."""

    def test_valid_input(self):
        """Test with valid input."""
        result = your_function("valid")
        assert result is not None

    def test_invalid_input(self):
        """Test with invalid input."""
        with pytest.raises(ValueError):
            your_function("")

    def test_edge_cases(self):
        """Test edge cases."""
        result = your_function("a" * 1000)  # Long input
        assert result is not None

class TestYourModel:
    """Test suite for YourModel."""

    def test_creation(self):
        """Test model creation."""
        model = YourModel(field1="test", field2=50)
        assert model.field1 == "test"

    def test_validation(self):
        """Test model validation."""
        with pytest.raises(ValueError):
            YourModel(field1="", field2=50)
```

### Smoke Tests

Create a smoke test for end-to-end functionality:

```python
# In backend/test_your_feature.py
"""Smoke test for your feature."""

def run_smoke_test():
    """Run basic functionality test."""
    from backend.services import your_function

    result = your_function("test_input")
    assert result is not None
    print("✓ Your feature smoke test passed")

if __name__ == "__main__":
    run_smoke_test()
```

Run with: `python -m backend.test_your_feature`

## 🔍 Code Review Checklist

Before submitting a PR, verify:

- [ ] All functions have docstrings with Args, Returns, Raises, Examples
- [ ] All functions have type hints
- [ ] All external calls are wrapped in try-except with logging
- [ ] All inputs are validated
- [ ] All tests pass: `python -m pytest tests/`
- [ ] Code compiles: `python -m compileall -q backend tests`
- [ ] All imports work: `python -c "from backend import *"`
- [ ] Logging configured: `logger = logging.getLogger(__name__)`
- [ ] No hardcoded secrets or credentials
- [ ] Documentation updated if needed
- [ ] README updated if applicable

## 📦 Dependency Management

### Adding Dependencies

Only add dependencies that are:

- Actively maintained
- Widely used and trusted
- Have minimal dependencies themselves

Process:

1. Justify why the dependency is needed
2. Specify exact version: `package==1.2.3`
3. Test compatibility with existing packages
4. Update README with new dependency
5. Document any new configuration needed

### Removing Dependencies

To remove a dependency:

1. Search for all usages: `grep -r "import package"`
2. Replace with alternative or inline implementation
3. Update requirements.txt
4. Update README
5. Test: `python -m compileall -q backend tests`

## 🐛 Bug Reports

When reporting a bug:

1. **Description**: Clear description of the issue
2. **Reproduction**: Steps to reproduce
3. **Expected**: What should happen
4. **Actual**: What actually happens
5. **Environment**: Python version, OS, dependencies
6. **Logs**: Relevant log output (if available)

Example:

```
Title: Gemini API returns invalid JSON for scene with special characters

Description:
When analyzing a scene with special Unicode characters, the API returns
invalid JSON that cannot be parsed.

Reproduction:
1. Call analyze_scene() with scene containing emoji
2. JSON parsing fails with "Expecting value: line 1 column X"

Expected:
Scene should be analyzed successfully, emoji handled gracefully.

Actual:
JSONDecodeError raised, exception not caught properly.

Logs:
ERROR - backend.services.scene_analyzer - JSON parsing failed: Invalid JSON
```

## 📚 Resources

- [Pydantic Docs](https://docs.pydantic.dev/)
- [Python Logging](https://docs.python.org/3/library/logging.html)
- [Google Gemini API](https://ai.google.dev/tutorials/python_quickstart)
- [ClickHouse Docs](https://clickhouse.com/docs)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

## ✅ Quality Metrics

Target metrics for production code:

- **Test Coverage**: ≥ 80% of business logic
- **Documentation**: 100% of public APIs
- **Error Handling**: 100% of external calls
- **Type Hints**: 100% of functions
- **Linting**: 0 errors when using pylint/flake8
- **Compilation**: 0 syntax errors

## 🤝 Getting Help

- Check existing issues and documentation first
- Search codebase for similar implementations
- Review comments and docstrings for context
- Ask in issues/discussions if stuck

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to SyncAgent! Your efforts help make this a better, more reliable platform for music synchronization.

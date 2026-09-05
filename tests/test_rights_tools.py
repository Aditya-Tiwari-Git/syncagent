from backend.models.track import Track
from backend.tools.rights_tools import validate_music_rights_tool


def track(**overrides):
    values = {
        'id': 'TRK-001',
        'title': 'Midnight Drive',
        'artist': 'Demo Artist',
        'genre': 'cinematic',
        'mood': 'dark',
        'bpm': 72,
        'energy': 2,
        'duration_seconds': 145,
        'instrumentation': 'piano, strings',
        'sync_available': True,
        'commercial_use': True,
        'territory': 'worldwide',
        'license_price': 500.0,
        'license_type': 'sync_demo',
    }
    values.update(overrides)
    return Track(**values)


def test_rights_pass():
    result = validate_music_rights_tool(track(), budget=800, territory='Worldwide')
    assert result['valid'] is True
    assert result['rejection_reasons'] == []


def test_rights_reject_over_budget_and_sync():
    result = validate_music_rights_tool(
        track(license_price=1500, sync_available=False),
        budget=800,
        territory='Worldwide',
    )
    assert result['valid'] is False
    assert any('exceeds the budget' in reason for reason in result['rejection_reasons'])
    assert any('Sync rights' in reason for reason in result['rejection_reasons'])


def test_rights_reject_territory():
    result = validate_music_rights_tool(track(territory='US'), budget=800, territory='Worldwide')
    assert result['valid'] is False
    assert 'territory' in result['rejection_reasons'][0].lower()

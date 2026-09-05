from fastapi.testclient import TestClient

from backend.api import app


client = TestClient(app)


def test_root_and_health():
    assert client.get('/').json() == {'name': 'SyncAgent', 'status': 'online'}
    assert client.get('/health').json() == {'status': 'healthy'}


def test_analyze_request_validation():
    response = client.post('/api/analyze', json={
        'scene_description': 'too short',
        'budget': 800,
        'territory': 'Worldwide',
        'top_k': 5,
    })
    assert response.status_code == 422


def test_analyze_request_model_accepts_demo_request(monkeypatch):
    async def fake_run_syncagent(**kwargs):
        return {
            'scene_analysis': {
                'mood': ['dark'], 'energy': 2, 'bpm_min': 55,
                'bpm_max': 75, 'genres': ['cinematic'],
                'instrumentation': ['piano'], 'pacing': 'slow',
                'scene_duration_seconds': 60,
            },
            'recommendations': [],
            'rejected_candidates': [],
            'total_candidates': 0,
            'disclaimer': 'Final licensing must be verified with the relevant rights holder.',
        }

    monkeypatch.setattr('backend.api.run_syncagent', fake_run_syncagent)
    response = client.post('/api/analyze', json={
        'scene_description': 'An exhausted detective walks through an empty street at night.',
        'budget': 800,
        'territory': 'Worldwide',
        'top_k': 5,
    })
    assert response.status_code == 200
    assert response.json()['success'] is True

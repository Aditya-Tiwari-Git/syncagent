from backend.services.report_service import generate_clearance_report


def test_report_generation_with_recommendations_and_rejections():
    report = generate_clearance_report(
        scene_description='<night scene>',
        budget=800,
        territory='Worldwide',
        scene_analysis={
            'mood': ['dark'],
            'energy': 2,
            'bpm_min': 55,
            'bpm_max': 75,
            'genres': ['cinematic'],
            'instrumentation': ['piano'],
            'pacing': 'slow',
        },
        recommendations=[{
            'track_id': 'TRK-001',
            'title': 'Midnight Drive',
            'artist': 'Demo Artist',
            'match_score': 94,
            'license_cost': 500,
            'reason': 'Slow piano supports the scene.',
            'pre_clearance_status': 'passes',
        }],
        rejected_candidates=[{
            'track_id': 'TRK-002',
            'title': 'Neon Rain',
            'match_score': 97,
            'reason': 'License cost exceeds configured budget.',
        }],
    )
    payload = report.getvalue()
    assert payload.startswith(b'%PDF')
    assert len(payload) > 1000


def test_report_generation_empty_state():
    report = generate_clearance_report(
        scene_description='A quiet scene with no suitable licensed music.',
        budget=50,
        territory='Worldwide',
        scene_analysis={},
        recommendations=[],
        rejected_candidates=[],
    )
    assert report.getvalue().startswith(b'%PDF')

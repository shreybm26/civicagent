from app.provider import GeminiProvider

def test_provider_without_key_fails_closed():
    result = GeminiProvider(api_key="").classify("pothole", {"road_issue": {}})
    assert result.service_id is None
    assert result.confidence == 0


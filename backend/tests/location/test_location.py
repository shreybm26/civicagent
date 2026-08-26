from app.tools.location import resolve_location


def test_jntu_alias_resolves_only_to_curated_data() -> None:
    result = resolve_location("Near JNTU Metro, Kukatpally")

    assert result.address == "JNTU Metro Station, Kukatpally, Hyderabad 500085"
    assert result.source == "curated_location"
    assert result.confidence == 0.98
    assert result.needs_clarification is False


def test_vague_or_unknown_location_requests_clarification() -> None:
    vague = resolve_location("near my house")
    unknown = resolve_location("behind the blue building")

    assert vague.address is None
    assert vague.needs_clarification is True
    assert unknown.address is None
    assert unknown.needs_clarification is True

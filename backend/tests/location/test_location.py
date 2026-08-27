from unittest.mock import patch

from app.tools.location import compose_location_query, resolve_location


def test_jntu_alias_resolves_only_to_curated_data() -> None:
    result = resolve_location("Near JNTU Metro, Kukatpally")

    assert result.address == "JNTU Metro Station, Kukatpally, Hyderabad 500085"
    assert result.source == "curated_location"
    assert result.confidence == 0.98
    assert result.needs_clarification is False


def test_vague_or_unknown_location_requests_clarification() -> None:
    vague = resolve_location("near my house")
    with patch("app.tools.location.nominatim_search", return_value=[]):
        unknown = resolve_location("behind the blue building")

    assert vague.address is None
    assert vague.needs_clarification is True
    assert unknown.address is None
    assert unknown.needs_clarification is True


def test_typed_place_is_geocoded_when_not_in_curated_list() -> None:
    hits = [
        {
            "lat": "12.8921",
            "lon": "77.6954",
            "display_name": "Junnasandra, Bengaluru, Karnataka, India",
        }
    ]
    result = resolve_location("in junnasandra, bengaluru", geocode=lambda _: hits)

    assert result.needs_clarification is False
    assert result.source == "geocoded"
    assert result.lat == 12.8921
    assert result.lng == 77.6954
    assert "Junnasandra" in (result.address or "")


def test_follow_up_landmark_reuses_previous_area() -> None:
    hits = [
        {
            "lat": "12.8924",
            "lon": "77.6580",
            "display_name": "Wipro Limited, Sarjapur Road, Bengaluru, Karnataka, India",
        }
    ]
    captured: list[str] = []

    def geocode(query: str):
        captured.append(query)
        return hits

    result = resolve_location(
        "near Wipro office",
        prior_query="in junnasandra, bengaluru",
        geocode=geocode,
    )

    assert captured == ["near Wipro office, in junnasandra, bengaluru"]
    assert result.source == "geocoded"
    assert result.address is not None


def test_compose_query_does_not_duplicate_context() -> None:
    assert compose_location_query("Junnasandra, Bengaluru", "in junnasandra, bengaluru") == "in junnasandra, bengaluru"
    assert compose_location_query("in junnasandra, bengaluru", "in junnasandra, bengaluru") == "in junnasandra, bengaluru"


def test_multiple_geocode_hits_ask_which_place() -> None:
    hits = [
        {"lat": "12.84", "lon": "77.66", "display_name": "Wipro Electronic City, Bengaluru, India"},
        {"lat": "12.97", "lon": "77.72", "display_name": "Wipro Whitefield, Bengaluru, India"},
    ]
    result = resolve_location("Wipro office, Bengaluru", geocode=lambda _: hits)

    assert result.address is None
    assert result.needs_clarification is True
    assert "Electronic City" in (result.message or "")
    assert "Whitefield" in (result.message or "")

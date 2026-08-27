from unittest.mock import patch

from app.tools.location import candidate_location_queries, compose_location_query, resolve_location, strip_location_filler


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

    assert captured[0] == "Wipro office, junnasandra, bengaluru"
    assert result.source == "geocoded"
    assert result.address is not None


def test_chat_phrasing_and_failed_typo_do_not_block_a_city_area() -> None:
    captured: list[str] = []
    hits = [
        {
            "lat": "13.1005",
            "lon": "77.5940",
            "display_name": "Yelahanka, Bengaluru, Karnataka, India",
        }
    ]

    def geocode(query: str):
        captured.append(query)
        if query == "Yelahanka, Bengaluru":
            return hits
        return []

    result = resolve_location(
        "my area is Yelahanka, Bengaluru",
        prior_query="Junnsandra",
        geocode=geocode,
    )

    assert captured == ["Yelahanka, Bengaluru"]
    assert result.source == "geocoded"
    assert result.lat == 13.1005
    assert "Yelahanka" in (result.address or "")


def test_strip_location_filler() -> None:
    assert strip_location_filler("my area is Yelahanka, Bengaluru") == "Yelahanka, Bengaluru"
    assert strip_location_filler("in junnasandra, bengaluru") == "junnasandra, bengaluru"


def test_compose_query_does_not_duplicate_context() -> None:
    assert compose_location_query("Junnasandra, Bengaluru", "in junnasandra, bengaluru") == "Junnasandra, Bengaluru"
    assert candidate_location_queries("Junnasandra, Bengaluru", "Junnsandra") == ["Junnasandra, Bengaluru"]


def test_multiple_geocode_hits_use_the_top_match() -> None:
    hits = [
        {"lat": "12.84", "lon": "77.66", "display_name": "Wipro Electronic City, Bengaluru, India"},
        {"lat": "12.97", "lon": "77.72", "display_name": "Wipro Whitefield, Bengaluru, India"},
    ]
    result = resolve_location("Wipro office, Bengaluru", geocode=lambda _: hits)

    assert result.needs_clarification is False
    assert result.source == "geocoded"
    assert "Electronic City" in (result.address or "")

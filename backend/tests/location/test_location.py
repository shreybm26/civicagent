from unittest.mock import patch

from app.tools.location import (
    candidate_location_queries,
    compose_location_query,
    is_within_hyderabad_bounds,
    mentions_outside_service_area,
    outside_service_area_message,
    resolve_location,
    strip_location_filler,
)


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


def test_outside_city_text_is_rejected() -> None:
    result = resolve_location(
        "Nexus Koramangala, Nexus Mall Parking, Lakkasandra, Bengaluru South City Corporation, Bengaluru"
    )

    assert result.address is None
    assert result.needs_clarification is True
    assert result.message == outside_service_area_message()


def test_bengaluru_geocode_hit_is_rejected_even_if_returned() -> None:
    hits = [
        {
            "lat": "12.8921",
            "lon": "77.6954",
            "display_name": "Junnasandra, Bengaluru, Karnataka, 560035, India",
        }
    ]
    result = resolve_location("in junnasandra, bengaluru", geocode=lambda _: hits)

    assert result.address is None
    assert result.needs_clarification is True
    assert result.message == outside_service_area_message()


def test_hyderabad_place_is_geocoded_when_not_in_curated_list() -> None:
    hits = [
        {
            "lat": "17.4180",
            "lon": "78.4570",
            "display_name": "Abids, Hyderabad, Telangana, India",
        }
    ]
    result = resolve_location("near abids clock tower", geocode=lambda _: hits)

    assert result.needs_clarification is False
    assert result.source == "geocoded"
    assert result.lat == 17.4180
    assert result.lng == 78.4570
    assert "Abids" in (result.address or "")


def test_follow_up_landmark_adds_hyderabad_context() -> None:
    hits = [
        {
            "lat": "17.4180",
            "lon": "78.4570",
            "display_name": "Abids, Hyderabad, Telangana, India",
        }
    ]
    captured: list[str] = []

    def geocode(query: str):
        captured.append(query)
        return hits

    result = resolve_location("near clock tower", prior_query="abids", geocode=geocode)

    assert captured[0] == "clock tower, abids"
    assert len(captured) == 1
    assert result.source == "geocoded"
    assert result.address is not None


def test_bengaluru_prior_query_is_not_reused() -> None:
    captured: list[str] = []

    def geocode(query: str):
        captured.append(query)
        return []

    result = resolve_location(
        "near Wipro office",
        prior_query="in junnasandra, bengaluru",
        geocode=geocode,
    )

    assert captured == []
    assert result.message == outside_service_area_message()


def test_strip_location_filler() -> None:
    assert strip_location_filler("my area is Yelahanka, Bengaluru") == "Yelahanka, Bengaluru"
    assert strip_location_filler("in junnasandra, bengaluru") == "junnasandra, bengaluru"


def test_compose_query_adds_hyderabad_context() -> None:
    assert compose_location_query("kukatpally housing board") == "kukatpally housing board, Hyderabad, Telangana"
    assert candidate_location_queries("kukatpally housing board") == [
        "kukatpally housing board, Hyderabad, Telangana",
        "kukatpally housing board",
    ]


def test_hyderabad_context_is_used_when_first_query_misses() -> None:
    captured: list[str] = []

    def geocode(query: str):
        captured.append(query)
        if "Hyderabad" in query:
            return [
                {
                    "lat": "17.4180",
                    "lon": "78.4570",
                    "display_name": "Abids, Hyderabad, Telangana, India",
                }
            ]
        return []

    result = resolve_location("abids clock tower", geocode=geocode)

    assert captured == ["abids clock tower, Hyderabad, Telangana"]
    assert result.source == "geocoded"


def test_multiple_geocode_hits_use_first_hyderabad_match() -> None:
    hits = [
        {"lat": "17.4180", "lon": "78.4570", "display_name": "Abids, Hyderabad, India"},
        {"lat": "17.3924", "lon": "78.4660", "display_name": "Nampally, Hyderabad, India"},
    ]
    result = resolve_location("abids area", geocode=lambda _: hits)

    assert result.needs_clarification is False
    assert result.source == "geocoded"
    assert "Abids" in (result.address or "")


def test_hyderabad_bounds() -> None:
    assert is_within_hyderabad_bounds(17.385, 78.4867) is True
    assert is_within_hyderabad_bounds(12.8921, 77.6954) is False


def test_mentions_outside_service_area() -> None:
    assert mentions_outside_service_area("Koramangala, Bengaluru") is True
    assert mentions_outside_service_area("Kukatpally, Hyderabad") is False

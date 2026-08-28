from app.copy.empathy import empathetic_location_prompt


def test_road_pothole_on_street() -> None:
    message = empathetic_location_prompt("road_issue", "There is a pothole on my street")
    assert "pothole on your street" in message


def test_garbage_not_collected() -> None:
    message = empathetic_location_prompt("garbage_issue", "Garbage has not been collected in my area")
    assert "hasn't been collected" in message


def test_streetlight_off_at_home() -> None:
    message = empathetic_location_prompt(
        "streetlight_issue",
        "The streetlight outside my house has been off for a week",
    )
    assert "outside your home" in message


def test_water_leak_near_building() -> None:
    message = empathetic_location_prompt("water_issue", "There is a water leak near my building")
    assert "near your building" in message


def test_injury_on_pothole_here() -> None:
    message = empathetic_location_prompt("road_issue", "I got hurt on the pot hole here")
    assert "got hurt" in message
    assert "landmark" in message


def test_injury_on_pothole_with_place() -> None:
    message = empathetic_location_prompt("road_issue", "I got hurt on a pothole near JNTU metro")
    assert "got hurt on that pothole" in message

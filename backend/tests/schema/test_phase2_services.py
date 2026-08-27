from app.collection.engine import CollectionEngine
from app.collection.resolver import CandidateResolver
from app.contracts import Candidate
from app.schemas.registry import SchemaRegistry
from app.services.router import ServiceRouter
from app.tools.image import ImageAnalyzer

schemas = SchemaRegistry().all()

def test_router_supports_five_services():
    router = ServiceRouter(schemas)
    assert router.route("water pipe leak", None).service_id == "water_issue"

def test_collection_returns_candidate():
    result = CollectionEngine().collect("Near JNTU Metro", schemas["road_issue"])
    assert result[0].field_id == "location" and result[0].source == "conversation"

def test_correction_wins_over_photo():
    candidates = [Candidate(field_id="severity", value="high", source="photo", confidence=.9), Candidate(field_id="severity", value="low", source="correction", confidence=1)]
    assert CandidateResolver().resolve(candidates)[0][0].value == "low"

def test_image_fixtures():
    from io import BytesIO

    from PIL import Image

    analyzer = ImageAnalyzer()
    assert analyzer.analyze("selfie.jpg", b"x").relevant is False
    buffer = BytesIO()
    Image.new("RGB", (8, 8), (32, 32, 32)).save(buffer, format="JPEG")
    readable = analyzer.analyze("pothole.jpg", buffer.getvalue())
    assert readable.relevant is True
    assert readable.candidates == []

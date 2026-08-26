from ..contracts import Candidate, ImageResult

class ImageAnalyzer:
    def analyze(self, filename: str, content: bytes, provider: str = "mock") -> ImageResult:
        name = filename.lower()
        if any(word in name for word in ("selfie", "face", "portrait")):
            return ImageResult(relevant=False, reason="The image appears to be a selfie, not civic evidence.")
        if any(word in name for word in ("pothole", "road", "street")):
            return ImageResult(relevant=True, reason="The image appears relevant to a road issue.", candidates=[Candidate(field_id="severity", value="high", source="photo", confidence=.82, reason="Visible road-surface damage in the uploaded image")])
        return ImageResult(relevant=True, reason="Image saved as evidence; no field was inferred.")

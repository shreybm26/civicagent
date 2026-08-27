from io import BytesIO

from PIL import Image, UnidentifiedImageError

from ..contracts import Candidate, ImageDetail, ImageResult

class ImageAnalyzer:
    def analyze(self, filename: str, content: bytes, provider: str = "mock") -> ImageResult:
        if not content:
            return ImageResult(relevant=False, reason="The uploaded image is empty.")
        try:
            with Image.open(BytesIO(content)) as image:
                image.verify()
        except (UnidentifiedImageError, OSError):
            return ImageResult(relevant=False, reason="The uploaded file is not a readable image.")
        # The mock provider deliberately makes no visual claims from filenames.
        return ImageResult(
            relevant=True,
            relevance_confidence=0.75,
            reason="The image was received and is available for civic review.",
            summary="No confident field could be extracted from this image in demo mode.",
        )

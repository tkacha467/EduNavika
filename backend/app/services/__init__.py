from backend.app.services.duplicate_detection import (
    ExactDuplicateDetector,
    SemanticDuplicateDetectorInterface,
    normalize_text,
    compute_text_hash,
)
from backend.app.services.event_recorder import EventRecorderService

__all__ = [
    "ExactDuplicateDetector",
    "SemanticDuplicateDetectorInterface",
    "normalize_text",
    "compute_text_hash",
    "EventRecorderService",
]

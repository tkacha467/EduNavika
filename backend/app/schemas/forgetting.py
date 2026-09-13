from typing import Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator
from backend.app.domain.enums import ForgettingSignalStatus


class ForgettingSignalBase(BaseModel):
    student_id: str
    topic_id: str
    evidence_type: str
    evidence_strength: Optional[str] = Field("MODERATE", description="Categorical evidence strength (WEAK, MODERATE, STRONG). NOT a probability.")
    prior_performance_reference: Optional[Dict[str, Any]] = None
    later_performance_reference: Optional[Dict[str, Any]] = None
    status: ForgettingSignalStatus = ForgettingSignalStatus.UNRESOLVED
    evidence_metadata: Optional[Dict[str, Any]] = None

    # Backward compatibility for aliases
    prior_performance_ref: Optional[Dict[str, Any]] = None
    later_performance_ref: Optional[Dict[str, Any]] = None
    confidence_metadata: Optional[Dict[str, Any]] = None

    @model_validator(mode="before")
    @classmethod
    def reconcile_legacy_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "prior_performance_ref" in data and "prior_performance_reference" not in data:
                data["prior_performance_reference"] = data["prior_performance_ref"]
            if "later_performance_ref" in data and "later_performance_reference" not in data:
                data["later_performance_reference"] = data["later_performance_ref"]
            if "confidence_metadata" in data and "evidence_metadata" not in data:
                data["evidence_metadata"] = data["confidence_metadata"]
        return data


class ForgettingSignalCreate(ForgettingSignalBase):
    pass


class ForgettingSignalResponse(BaseModel):
    id: str
    student_id: str
    topic_id: str
    evidence_type: str
    evidence_strength: Optional[str] = None
    prior_performance_reference: Optional[Dict[str, Any]] = None
    later_performance_reference: Optional[Dict[str, Any]] = None
    status: ForgettingSignalStatus
    evidence_metadata: Optional[Dict[str, Any]] = None
    detected_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

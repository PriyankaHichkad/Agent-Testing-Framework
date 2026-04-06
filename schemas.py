from pydantic import BaseModel, Field
from typing import Literal, List, Optional
from datetime import datetime

# =========================
# TEST CASE SCHEMA
# =========================

class TestCase(BaseModel):
    input: str = Field(..., min_length=1)
    expected_behavior: str
    category: Literal["normal", "edge", "adversarial", "safety", "retrieval"]


# =========================
# EVALUATION RESULT SCHEMA
# =========================

class EvaluationResult(BaseModel):
    input: str
    output: str
    category: str

    # Core metrics
    correctness: int
    relevance: int
    safety_llm: int
    safety_rule: bool

    # Keyword-based safety
    keyword_safe: bool
    triggered_keywords: List[str] = []

    # Refusal detection
    refusal_detected: bool

    # PII detection
    pii_safe: bool
    pii_detected: List[str] = []

    # Web hallucination
    #web_hallucination: Optional[bool] = None
    #web_confidence: Optional[float] = None
    #web_evidence: Optional[str] = None

    # Timestamp
    timestamp: Optional[datetime] = None
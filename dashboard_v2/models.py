from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class ExtractedMetric(BaseModel):
    company: str
    metric_name: str
    value: float
    period_end: str
    fiscal_label: str
    unit_scale: str
    raw_text: str
    source_snippet: str
    source_location: str
    extractor: Literal["parser", "llm"]
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_signals: Dict[str, Any] = Field(default_factory=dict)
    status: Literal["APPROVED", "FLAGGED", "REJECTED"] = "APPROVED"


class ValidationResult(BaseModel):
    check_name: str
    status: Literal["PASSED", "FAILED", "NOT_APPLICABLE"]
    reason: str
    metrics_involved: List[str]


class ReviewItem(BaseModel):
    id: str
    thread_id: str
    metric: str
    reason: str
    status: Literal["PENDING", "DONE"]
    created_at: str


class AuditEntry(BaseModel):
    audit_id: str
    thread_id: str
    company: str
    metric: str
    original_value: float
    final_value: Optional[float]
    decision: Literal["APPROVED", "CORRECTED", "REJECTED"]
    reviewer_notes: str
    reviewer_id: str
    simulated: bool
    timestamp: str


class Config(BaseModel):
    confidence_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    year_on_year_threshold: float = Field(default=0.25, ge=0.0, le=2.0)
    equation_tolerance: float = Field(default=0.01, ge=0.0, le=0.1)
    spot_check_rate: float = Field(default=0.10, ge=0.0, le=1.0)


class RunState(BaseModel):
    thread_id: str
    ticker: str
    company_name: str
    workflow_status: Literal["RUNNING", "PAUSED_FOR_REVIEW", "COMPLETED"]
    data_source: Literal["SAMPLE", "CACHE", "LIVE_SEC"]
    fault_injected: bool = False
    metrics: List[ExtractedMetric]
    validations: List[ValidationResult]


class MetricAccuracyRow(BaseModel):
    metric_name: str
    extracted_value: float
    ground_truth_value: float
    error_pct: float
    accurate: bool


class ReportResponse(BaseModel):
    thread_id: str
    company: str
    extraction_accuracy_pct: float
    escalation_precision_pct: float
    auto_approved_count: int
    escalated_count: int
    per_metric_accuracy: List[MetricAccuracyRow]
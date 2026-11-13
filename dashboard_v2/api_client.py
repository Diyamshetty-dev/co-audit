import os
from typing import Any, Dict, List, Literal, Optional, Protocol

import requests

from models import (
    AuditEntry,
    Config,
    MetricAccuracyRow,
    ReportResponse,
    ReviewItem,
    RunState,
)

WORKFLOW_STATUS = {"PAUSED": "PAUSED_FOR_REVIEW", "COMPLETED": "COMPLETED"}
DECISION_STATUS = {"APPROVED": "APPROVED", "CORRECTED": "APPROVED", "REJECTED": "REJECTED"}
EXTRACTOR_LABEL = {"parser": "parser", "llm": "llm", "derived": "parser"}
DEFAULT_EQUATION_TOLERANCE = 0.01


class AuditClientProtocol(Protocol):
    def get_config(self) -> Config: ...
    def update_config(self, config: Config) -> Config: ...
    def start_run(self, ticker: str, fault_switch: bool = False) -> str: ...
    def get_run(self, thread_id: str) -> RunState: ...
    def list_reviews(self, status: Literal["PENDING", "DONE"], thread_id: Optional[str] = None) -> List[ReviewItem]: ...
    def submit_decision(
        self,
        review_id: str,
        action: Literal["APPROVED", "CORRECTED", "REJECTED"],
        corrected_value: Optional[float],
        notes: str,
        reviewer_id: str,
    ) -> ReviewItem: ...
    def get_audit_log(self, thread_id: Optional[str] = None) -> List[AuditEntry]: ...
    def get_report(self, thread_id: str) -> ReportResponse: ...


def describe_location(metric: Dict[str, Any]) -> str:
    derived = metric.get("derived_from") or []
    if metric.get("extractor") == "derived" and derived:
        return "derived from " + ", ".join(derived)
    location = metric.get("source_location")
    if not location:
        return "not recorded"
    text = f"table {location['table_id']}, row {location['row_index']}"
    if location.get("column_index") is not None:
        text += f", column {location['column_index']}"
    return text


def percent_error(extracted: float, truth: float) -> float:
    if truth:
        return abs(extracted - truth) / abs(truth) * 100.0
    return 0.0 if extracted == 0 else 100.0


def convert_config(data: Dict[str, Any]) -> Config:
    return Config(
        confidence_threshold=data["confidence_threshold"],
        year_on_year_threshold=data["year_on_year_threshold"],
        equation_tolerance=DEFAULT_EQUATION_TOLERANCE,
        spot_check_rate=data["spot_check_rate"],
    )


def convert_metric(
    metric: Dict[str, Any], flagged: bool, latest: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    status = "FLAGGED" if flagged else "APPROVED"
    value = metric["value"]
    if latest is not None:
        status = DECISION_STATUS[latest["decision"]]
        if latest["decision"] == "CORRECTED" and latest["final_value"] is not None:
            value = latest["final_value"]
    return {
        "company": metric["company"],
        "metric_name": metric["metric_name"],
        "value": value,
        "period_end": str(metric["period_end"]),
        "fiscal_label": metric["fiscal_label"],
        "unit_scale": str(metric["unit_scale"]),
        "raw_text": metric["raw_text"],
        "source_snippet": metric["source_snippet"],
        "source_location": describe_location(metric),
        "extractor": EXTRACTOR_LABEL[metric["extractor"]],
        "confidence": metric.get("confidence") or 0.0,
        "confidence_signals": metric.get("confidence_signals") or {},
        "status": status,
    }


def convert_review(item: Dict[str, Any]) -> ReviewItem:
    return ReviewItem(
        id=item["id"],
        thread_id=item["thread_id"],
        metric=item["metric_name"],
        reason=item["reason"],
        status=item["status"],
        created_at=str(item["created_at"]),
    )


def convert_audit(entry: Dict[str, Any]) -> AuditEntry:
    return AuditEntry(
        audit_id=str(entry["audit_id"]),
        thread_id=entry["thread_id"],
        company=entry["company"],
        metric=entry["metric_name"],
        original_value=entry["original_value"],
        final_value=entry["final_value"],
        decision=entry["decision"],
        reviewer_notes=entry["reviewer_notes"],
        reviewer_id=entry["reviewer_id"],
        simulated=entry["simulated"],
        timestamp=str(entry["timestamp"]),
    )


class HttpAuditClient:
    def __init__(self, base_url: str, timeout: float = 120.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _check(self, response: requests.Response) -> Any:
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except ValueError:
                detail = response.text
            raise RuntimeError(f"{response.status_code}: {detail}")
        return response.json()

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        response = requests.get(f"{self.base_url}{path}", params=params, timeout=min(self.timeout, 10.0))
        return self._check(response)

    def _send(self, method: str, path: str, body: Dict[str, Any]) -> Any:
        response = requests.request(method, f"{self.base_url}{path}", json=body, timeout=self.timeout)
        return self._check(response)

    def get_config(self) -> Config:
        return convert_config(self._get("/config"))

    def update_config(self, config: Config) -> Config:
        current = self._get("/config")
        current["confidence_threshold"] = config.confidence_threshold
        current["year_on_year_threshold"] = config.year_on_year_threshold
        current["spot_check_rate"] = config.spot_check_rate
        return convert_config(self._send("PUT", "/config", current))

    def start_run(self, ticker: str, fault_switch: bool = False) -> str:
        run = self._send("POST", "/runs", {"ticker": ticker, "fault_switch": fault_switch})
        return run["thread_id"]

    def get_run(self, thread_id: str) -> RunState:
        run = self._get(f"/runs/{thread_id}")
        if run["status"] == "FAILED":
            raise RuntimeError(run["error"] or "The run failed")
        latest = {entry["metric_name"]: entry for entry in self._get("/audit", {"thread_id": thread_id})}
        flagged = {item["metric_name"] for item in run["decisions"] if item["flagged"]}
        return RunState(
            thread_id=thread_id,
            ticker=run["ticker"],
            company_name=run["company"] or run["ticker"],
            workflow_status=WORKFLOW_STATUS.get(run["status"], "RUNNING"),
            data_source=run["data_source"] or "LIVE_SEC",
            fault_injected=run["fault_injected"],
            metrics=[
                convert_metric(metric, metric["metric_name"] in flagged, latest.get(metric["metric_name"]))
                for metric in run["metrics"]
            ],
            validations=[
                {
                    "check_name": item["check_name"],
                    "status": item["status"],
                    "reason": item["reason"],
                    "metrics_involved": list(item["metrics_involved"]),
                }
                for item in run["validations"]
            ],
        )

    def list_reviews(
        self,
        status: Literal["PENDING", "DONE"],
        thread_id: Optional[str] = None,
    ) -> List[ReviewItem]:
        params: Dict[str, Any] = {"status": status}
        if thread_id:
            params["thread_id"] = thread_id
        return [convert_review(item) for item in self._get("/reviews", params)]

    def submit_decision(
        self,
        review_id: str,
        action: Literal["APPROVED", "CORRECTED", "REJECTED"],
        corrected_value: Optional[float],
        notes: str,
        reviewer_id: str,
    ) -> ReviewItem:
        payload = {
            "action": action,
            "corrected_value": corrected_value,
            "notes": notes,
            "reviewer_id": reviewer_id,
        }
        result = self._send("POST", f"/reviews/{review_id}/decision", payload)
        entry = result["audit_entry"]
        done = self._get("/reviews", {"status": "DONE", "thread_id": entry["thread_id"]})
        match = next((item for item in done if item["id"] == review_id), None)
        if match is not None:
            return convert_review(match)
        return ReviewItem(
            id=review_id,
            thread_id=entry["thread_id"],
            metric=entry["metric_name"],
            reason="",
            status="DONE",
            created_at=str(entry["timestamp"]),
        )

    def get_audit_log(self, thread_id: Optional[str] = None) -> List[AuditEntry]:
        params = {"thread_id": thread_id} if thread_id else None
        return [convert_audit(entry) for entry in self._get("/audit", params)]

    def get_report(self, thread_id: str) -> ReportResponse:
        data = self._get(f"/report/{thread_id}")
        run = self._get(f"/runs/{thread_id}")
        report = data["report"] or {}
        rows = [
            MetricAccuracyRow(
                metric_name=outcome["metric_name"],
                extracted_value=outcome["extracted_value"],
                ground_truth_value=outcome["truth_value"],
                error_pct=round(percent_error(outcome["extracted_value"], outcome["truth_value"]), 4),
                accurate=bool(outcome["is_correct"]),
            )
            for outcome in report.get("outcomes", [])
            if outcome["truth_value"] is not None
        ]
        return ReportResponse(
            thread_id=thread_id,
            company=run["company"] or run["ticker"],
            extraction_accuracy_pct=round(100.0 * (report.get("overall_accuracy") or 0.0), 2),
            escalation_precision_pct=round(100.0 * (report.get("escalation_precision") or 0.0), 2),
            auto_approved_count=report.get("auto_approved_count", 0),
            escalated_count=report.get("escalated_count", 0),
            per_metric_accuracy=rows,
        )


def build_client(use_mock: bool = True, base_url: Optional[str] = None) -> AuditClientProtocol:
    if use_mock:
        from mock_client import MockAuditClient
        return MockAuditClient()
    resolved_url = base_url or os.getenv("CO_AUDIT_API_URL", "http://192.168.1.222:8000")
    return HttpAuditClient(base_url=resolved_url)

import csv
import html
import io
import math
import re
from typing import Dict, List, Optional, Tuple

from models import AuditEntry, Config, ExtractedMetric, ReportResponse, RunState, ValidationResult

TWO_PERSON_LIMIT_USD = 150_000_000_000.0

STATEMENT_GROUPS = {
    "Income Statement": ["Revenue", "Gross Profit", "Operating Income", "Net Income"],
    "Balance Sheet": ["Total Assets", "Total Liabilities", "Shareholders' Equity"],
    "Cash Flow Statement": ["Operating Cash Flow"],
}

PIPELINE_STEPS = ["Fetch", "Extract", "Validate", "Human review", "Verify and log"]


def format_usd(amount: Optional[float]) -> str:
    if amount is None:
        return "N/A"
    magnitude = abs(amount)
    sign = "-" if amount < 0 else ""
    if magnitude >= 1e9:
        return f"{sign}${magnitude / 1e9:,.2f}B"
    if magnitude >= 1e6:
        return f"{sign}${magnitude / 1e6:,.2f}M"
    return f"{sign}${magnitude:,.2f}"


def parse_numeric_input(raw_text: str) -> Optional[float]:
    cleaned = raw_text.strip().replace(",", "").replace("$", "")
    if not cleaned:
        return None
    try:
        value = float(cleaned)
    except ValueError:
        return None
    if value != value or value in (float("inf"), float("-inf")):
        return None
    return value


def display_name(raw: str) -> str:
    if " " in raw or raw != raw.lower():
        return raw
    text = " ".join(word.capitalize() for word in raw.replace("_", " ").split())
    return text.replace("Shareholders Equity", "Shareholders' Equity")


def display_company(name: str) -> str:
    return name.title() if name.isupper() else name


def short_text(text: str, limit: int = 44) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "..."


def status_pill_html(status: str) -> str:
    normalized = status.upper()
    if normalized in ("APPROVED", "PASSED"):
        css = "pill-approved"
    elif normalized == "FLAGGED":
        css = "pill-flagged"
    elif normalized in ("REJECTED", "FAILED"):
        css = "pill-rejected"
    else:
        css = "pill-na"
    label = normalized.replace("_", " ")
    return f'<span class="pill {css}">{html.escape(label)}</span>'


def confidence_bar_html(score: float, threshold: float) -> str:
    percent = max(0, min(100, int(round(score * 100))))
    color = "#0E9F8E" if score >= threshold else "#F4A62A"
    return (
        '<div class="conf-wrap">'
        f'<div class="conf-track"><div class="conf-fill" style="width:{percent}%;background:{color};"></div></div>'
        f"<span><strong>{score:.2f}</strong></span>"
        "</div>"
    )


def metric_checks_html(metric_name: str, validations: List[ValidationResult]) -> str:
    parts: List[str] = []
    for validation in validations:
        if metric_name in validation.metrics_involved:
            parts.append(
                '<div class="check-line">'
                f"{status_pill_html(validation.status)} "
                f"<strong>{html.escape(validation.check_name.replace('_', ' '))}:</strong> "
                f"{html.escape(validation.reason)}"
                "</div>"
            )
    if not parts:
        return f'<div class="check-line">{status_pill_html("NOT_APPLICABLE")} No rule triggered</div>'
    return "".join(parts)


def materiality_score(metric: ExtractedMetric, validations: List[ValidationResult]) -> float:
    has_failed_check = any(
        v.status == "FAILED" and metric.metric_name in v.metrics_involved for v in validations
    )
    risk = max(0.05, 1.0 - metric.confidence) + (0.50 if has_failed_check else 0.0)
    return risk * abs(metric.value)


def pipeline_stepper_html(workflow_status: str) -> str:
    if workflow_status == "COMPLETED":
        active_index = len(PIPELINE_STEPS)
    elif workflow_status == "PAUSED_FOR_REVIEW":
        active_index = 3
    else:
        active_index = 1
    items: List[str] = []
    for index, label in enumerate(PIPELINE_STEPS):
        if index < active_index:
            state = "step-done"
            mark = "&#10003;"
        elif index == active_index:
            state = "step-active"
            mark = str(index + 1)
        else:
            state = "step-pending"
            mark = str(index + 1)
        items.append(
            f'<div class="step {state}"><div class="step-dot">{mark}</div>'
            f'<div class="step-label">{html.escape(label)}</div></div>'
        )
    return '<div class="stepper">' + '<div class="step-link"></div>'.join(items) + "</div>"


def kpi_html(label: str, value: str, hint: str = "") -> str:
    hint_html = f'<div class="kpi-hint">{html.escape(hint)}</div>' if hint else ""
    return (
        '<div class="kpi-card">'
        f'<div class="kpi-label">{html.escape(label)}</div>'
        f'<div class="kpi-value">{html.escape(value)}</div>'
        f"{hint_html}"
        "</div>"
    )


def metrics_table_html(run: RunState, config: Config) -> str:
    rows: List[str] = []
    for metric in run.metrics:
        dual_badge = (
            ' <span class="badge badge-dual">2-person limit</span>'
            if abs(metric.value) >= TWO_PERSON_LIMIT_USD and metric.status == "FLAGGED"
            else ""
        )
        row_class = ' class="row-flagged"' if metric.status == "FLAGGED" else ""
        rows.append(
            f"<tr{row_class}>"
            f"<td><strong>{html.escape(display_name(metric.metric_name))}</strong>{dual_badge}"
            f"<br><small>{html.escape(metric.fiscal_label)} &middot; {html.escape(metric.extractor.upper())}</small></td>"
            f"<td><strong>{format_usd(metric.value)}</strong><br><small>{html.escape(short_text(metric.raw_text))}</small></td>"
            f"<td>{status_pill_html(metric.status)}</td>"
            f"<td>{confidence_bar_html(metric.confidence, config.confidence_threshold)}</td>"
            f"<td>{metric_checks_html(metric.metric_name, run.validations)}</td>"
            "</tr>"
        )
    return (
        '<div class="table-scroll"><table class="metrics-table"><colgroup><col style="width:18%"><col style="width:17%">'
        '<col style="width:13%"><col style="width:14%"><col style="width:38%"></colgroup><thead><tr>'
        "<th>Metric</th><th>Extracted value</th><th>Status</th><th>Confidence</th><th>Validation checks</th>"
        f"</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
    )


def click_to_source_html(run: RunState, target_metric: str) -> str:
    selected_group = "Financial Statement"
    selected_names = [display_name(m.metric_name) for m in run.metrics]
    for title, names in STATEMENT_GROUPS.items():
        if display_name(target_metric) in names:
            selected_group = title
            selected_names = names
            break
    rows: List[str] = []
    for metric in run.metrics:
        if display_name(metric.metric_name) not in selected_names:
            continue
        is_target = metric.metric_name == target_metric
        row_class = ' class="filing-row-highlight"' if is_target else ""
        cell = f"{html.escape(metric.raw_text)} ({format_usd(metric.value)})"
        if is_target:
            cell = f'<span class="filing-cell-highlight">{cell}</span>'
        rows.append(
            f"<tr{row_class}><td>{html.escape(display_name(metric.metric_name))}</td><td>{cell}</td>"
            f"<td>{html.escape(metric.source_location)}</td></tr>"
        )
    return (
        '<table class="filing-table"><thead><tr>'
        f"<th>{html.escape(selected_group)} line item</th><th>Extracted cell</th><th>10-K location</th>"
        f"</tr></thead><tbody>{''.join(rows)}</tbody></table>"
    )


def build_escalation_points(run: RunState, report: ReportResponse) -> List[Dict[str, float]]:
    truth_by_name = {r.metric_name: r.ground_truth_value for r in report.per_metric_accuracy}
    failed_names = {
        name for v in run.validations if v.status == "FAILED" for name in v.metrics_involved
    }
    is_error: Dict[str, bool] = {}
    for metric in run.metrics:
        truth = truth_by_name.get(metric.metric_name)
        reference = truth if truth is not None else metric.value
        differs = abs(metric.value - reference) / max(abs(reference), 1.0) > 0.005
        is_error[metric.metric_name] = differs or metric.metric_name in failed_names
    total = max(len(run.metrics), 1)
    total_errors = sum(1 for flag in is_error.values() if flag)
    points: List[Dict[str, float]] = []
    for step in range(50, 101, 5):
        threshold = step / 100.0
        reviewed = [
            m.metric_name
            for m in run.metrics
            if m.confidence < threshold or m.metric_name in failed_names
        ]
        caught = sum(1 for name in reviewed if is_error.get(name, False))
        points.append(
            {
                "threshold": threshold,
                "reviewed": round(len(reviewed) / total * 100.0, 1),
                "caught": round((caught / total_errors * 100.0) if total_errors else 100.0, 1),
            }
        )
    return points


def build_workpaper_csv(run: RunState, report: ReportResponse, audit_entries: List[AuditEntry]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Co Audit Workpaper", run.company_name, run.ticker, run.thread_id, run.data_source])
    writer.writerow([])
    writer.writerow(["Metric", "Final Value (USD)", "Ground Truth (USD)", "Error %", "Status", "Confidence"])
    truth_rows = {r.metric_name: r for r in report.per_metric_accuracy}
    for metric in run.metrics:
        row = truth_rows.get(metric.metric_name)
        writer.writerow(
            [
                metric.metric_name,
                metric.value,
                row.ground_truth_value if row else "",
                row.error_pct if row else "",
                metric.status,
                metric.confidence,
            ]
        )
    writer.writerow([])
    writer.writerow(["Audit ID", "Timestamp", "Metric", "Original", "Final", "Decision", "Reviewer", "Notes", "Simulated"])
    for entry in audit_entries:
        writer.writerow(
            [
                entry.audit_id,
                entry.timestamp,
                entry.metric,
                entry.original_value,
                entry.final_value if entry.final_value is not None else "REJECTED",
                entry.decision,
                entry.reviewer_id,
                entry.reviewer_notes,
                entry.simulated,
            ]
        )
    return buffer.getvalue()


def build_workpaper_html(run: RunState, report: ReportResponse, audit_entries: List[AuditEntry]) -> str:
    metric_rows = "".join(
        f"<tr><td>{html.escape(m.metric_name)}</td><td>{format_usd(m.value)}</td>"
        f"<td>{html.escape(m.status)}</td><td>{m.confidence:.2f}</td></tr>"
        for m in run.metrics
    )
    audit_rows = "".join(
        f"<tr><td>{html.escape(e.audit_id)}</td><td>{html.escape(e.timestamp)}</td>"
        f"<td>{html.escape(e.metric)}</td><td>{html.escape(e.decision)}</td>"
        f"<td>{html.escape(e.reviewer_id)}</td><td>{html.escape(e.reviewer_notes)}</td></tr>"
        for e in audit_entries
    )
    return (
        f"<html><head><meta charset='utf-8'><title>Co Audit Workpaper - {html.escape(run.ticker)}</title>"
        "<style>body{font-family:Arial,sans-serif;padding:24px;color:#0B1F3A;}"
        "table{border-collapse:collapse;width:100%;margin-bottom:20px;}"
        "th,td{border:1px solid #C8D6E5;padding:8px;text-align:left;}"
        "th{background:#16365F;color:#fff;}</style></head><body>"
        f"<h1>Co Audit Workpaper - {html.escape(run.company_name)} ({html.escape(run.ticker)})</h1>"
        f"<p>Thread: {html.escape(run.thread_id)} | Source: {html.escape(run.data_source)} | "
        f"Extraction accuracy: {report.extraction_accuracy_pct:.1f}% | "
        f"Escalation precision: {report.escalation_precision_pct:.1f}%</p>"
        "<h2>Extracted metrics</h2><table><thead><tr><th>Metric</th><th>Final value</th><th>Status</th><th>Confidence</th></tr></thead>"
        f"<tbody>{metric_rows}</tbody></table>"
        "<h2>Append-only audit trail</h2><table><thead><tr><th>Audit ID</th><th>Timestamp</th><th>Metric</th><th>Decision</th><th>Reviewer</th><th>Notes</th></tr></thead>"
        f"<tbody>{audit_rows}</tbody></table></body></html>"
    )


def confidence_ring_html(score: float, threshold: float) -> str:
    clamped = max(0.0, min(1.0, score))
    radius = 34.0
    circumference = 2 * math.pi * radius
    filled = circumference * clamped
    color = "#0E9F8E" if score >= threshold else "#F4A62A"
    return (
        '<div class="ring-wrap"><svg viewBox="0 0 84 84" width="84" height="84">'
        f'<circle cx="42" cy="42" r="{radius}" fill="none" stroke="#E3EAF3" stroke-width="9"/>'
        f'<circle cx="42" cy="42" r="{radius}" fill="none" stroke="{color}" stroke-width="9" stroke-linecap="round" '
        f'stroke-dasharray="{filled:.1f} {circumference:.1f}" transform="rotate(-90 42 42)"/>'
        f'<text x="42" y="47" text-anchor="middle" font-size="17" font-weight="700" fill="#0B1F3A">{score:.2f}</text>'
        "</svg>"
        f'<div class="ring-label">Confidence<br><small>Threshold {threshold:.2f}</small></div></div>'
    )


def user_chip_html(name: str, role: str, compact: bool = False) -> str:
    parts = [part for part in re.split(r"[\s_\-]+", name.strip()) if part]
    initials = "".join(part[0] for part in parts)[:2].upper() or "R"
    safe_name = html.escape(name)
    safe_role = html.escape(role)
    if compact:
        return (
            f'<span class="header-user"><span class="avatar">{initials}</span>'
            f'<span><span class="user-name">{safe_name}</span><br><span class="user-role">{safe_role}</span></span></span>'
        )
    return (
        f'<div class="user-chip"><span class="avatar">{initials}</span>'
        f'<div><div class="user-name">{safe_name}</div><div class="user-role">{safe_role}</div></div></div>'
    )


def validation_list_html(validations: List[ValidationResult]) -> str:
    passed = sum(1 for v in validations if v.status == "PASSED")
    failed = sum(1 for v in validations if v.status == "FAILED")
    other = len(validations) - passed - failed
    summary = (
        '<div class="checks-summary">'
        f'<span class="pill pill-approved">{passed} passed</span>'
        f'<span class="pill pill-rejected">{failed} failed</span>'
        f'<span class="pill pill-na">{other} not applicable</span>'
        "</div>"
    )
    rows: List[str] = []
    for validation in validations:
        name = html.escape(validation.check_name.replace("_", " ").title())
        involved = ", ".join(display_name(m) for m in validation.metrics_involved)
        rows.append(
            '<div class="checks-row">'
            f"<div>{status_pill_html(validation.status)}</div>"
            f'<div class="checks-name">{name}<br><small>{html.escape(short_text(involved, 40))}</small></div>'
            f'<div class="checks-reason">{html.escape(validation.reason)}</div>'
            "</div>"
        )
    return f'<div class="section-card">{summary}{"".join(rows)}</div>'


def split_check_counts(validations: List[ValidationResult]) -> Tuple[int, int, int]:
    passed = sum(1 for v in validations if v.status == "PASSED")
    failed = sum(1 for v in validations if v.status == "FAILED")
    other = len(validations) - passed - failed
    return passed, failed, other

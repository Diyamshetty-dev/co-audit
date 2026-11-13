import html
import os
from typing import Dict, List, Optional

import altair as alt
import pandas as pd
import streamlit as st

from api_client import AuditClientProtocol, build_client
from helpers import (
    TWO_PERSON_LIMIT_USD,
    build_escalation_points,
    build_workpaper_csv,
    build_workpaper_html,
    click_to_source_html,
    confidence_bar_html,
    confidence_ring_html,
    display_company,
    display_name,
    format_usd,
    kpi_html,
    materiality_score,
    metric_checks_html,
    metrics_table_html,
    parse_numeric_input,
    pipeline_stepper_html,
    status_pill_html,
    user_chip_html,
    validation_list_html,
)
from landing import render_login
from models import Config, ExtractedMetric, ReportResponse, RunState
from styles import apply_custom_styles

COMPANIES: Dict[str, str] = {
    "AAPL": "Apple Inc. (AAPL)",
    "MSFT": "Microsoft Corporation (MSFT)",
    "NVDA": "NVIDIA Corporation (NVDA)",
    "WMT": "Walmart Inc. (WMT)",
    "TSLA": "Tesla, Inc. (TSLA)",
    "COST": "Costco Wholesale Corporation (COST)",
    "AMZN": "Amazon.com, Inc. (AMZN)",
    "KO": "The Coca-Cola Company (KO)",
}


def stretch_options() -> Dict[str, object]:
    parts = st.__version__.split(".")
    try:
        major, minor = int(parts[0]), int(parts[1])
    except (ValueError, IndexError):
        return {"use_container_width": True}
    if (major, minor) >= (1, 50):
        return {"width": "stretch"}
    return {"use_container_width": True}


STRETCH = stretch_options()


def init_state() -> None:
    defaults = {
        "backend_mode": "Sample Data" if os.environ.get("CO_AUDIT_MODE", "").lower() == "sample" else "Live FastAPI",
        "api_url": os.environ.get("CO_AUDIT_API_URL", "http://127.0.0.1:8000"),
        "active_thread_id": None,
        "reviewer_id": "",
        "reviewer_role": "Reviewer",
        "signed_in": False,
        "requested_ticker": None,
        "fault_switch": False,
        "first_approvals": {},
        "flash_message": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if "mock_client" not in st.session_state:
        st.session_state.mock_client = build_client(use_mock=True)


def get_active_client() -> AuditClientProtocol:
    if st.session_state.backend_mode == "Sample Data":
        return st.session_state.mock_client
    return build_client(use_mock=False, base_url=st.session_state.api_url)


def source_badge_html(data_source: str) -> str:
    if data_source == "SAMPLE":
        return '<span class="badge badge-sample">Sample data</span>'
    if data_source == "CACHE":
        return '<span class="badge badge-cache">From cache</span>'
    return '<span class="badge badge-live">Live SEC EDGAR</span>'


def load_report(client: AuditClientProtocol, thread_id: str) -> Optional[ReportResponse]:
    try:
        return client.get_report(thread_id)
    except Exception:
        return None


def escalation_chart(points: List[Dict[str, float]], current_threshold: float) -> alt.Chart:
    frame = pd.DataFrame(points)
    nearest = frame.iloc[(frame["threshold"] - current_threshold).abs().argsort().iloc[0]]
    x_axis = alt.X("reviewed:Q", title="Share of values reviewed (%)", scale=alt.Scale(domain=[0, 100]))
    y_axis = alt.Y("caught:Q", title="Share of errors caught (%)", scale=alt.Scale(domain=[0, 100]))
    baseline = (
        alt.Chart(pd.DataFrame({"x": [0, 100], "y": [0, 100]}))
        .mark_line(strokeDash=[6, 5], color="#9AA9BC")
        .encode(x="x:Q", y="y:Q")
    )
    line = (
        alt.Chart(frame)
        .mark_line(color="#2F6FD0", strokeWidth=3, interpolate="monotone")
        .encode(x=x_axis, y=y_axis)
    )
    dots = (
        alt.Chart(frame)
        .mark_circle(color="#2F6FD0", size=70)
        .encode(
            x=x_axis,
            y=y_axis,
            tooltip=[
                alt.Tooltip("threshold:Q", title="Confidence threshold"),
                alt.Tooltip("reviewed:Q", title="Reviewed (%)"),
                alt.Tooltip("caught:Q", title="Errors caught (%)"),
            ],
        )
    )
    current = (
        alt.Chart(pd.DataFrame([nearest]))
        .mark_point(color="#F4A62A", size=260, filled=True, stroke="#0B1F3A", strokeWidth=2)
        .encode(x="reviewed:Q", y="caught:Q")
    )
    return (baseline + line + dots + current).properties(height=320).configure_view(strokeWidth=0)


def accuracy_chart(report: ReportResponse) -> alt.Chart:
    frame = pd.DataFrame(
        [
            {
                "Metric": display_name(row.metric_name),
                "Error (%)": row.error_pct,
                "Result": "Matches SEC data" if row.accurate else "Differs from SEC data",
            }
            for row in report.per_metric_accuracy
        ]
    )
    return (
        alt.Chart(frame)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            y=alt.Y("Metric:N", sort=None, title=None),
            x=alt.X("Error (%):Q", title="Difference from SEC XBRL value (%)"),
            color=alt.Color(
                "Result:N",
                scale=alt.Scale(
                    domain=["Matches SEC data", "Differs from SEC data"],
                    range=["#0E9F8E", "#D9473F"],
                ),
                legend=alt.Legend(orient="bottom", title=None),
            ),
            tooltip=["Metric", "Error (%)", "Result"],
        )
        .properties(height=300)
        .configure_view(strokeWidth=0)
    )


def handling_chart(report: ReportResponse) -> alt.Chart:
    frame = pd.DataFrame(
        [
            {"Outcome": "Auto-approved", "Count": report.auto_approved_count},
            {"Outcome": "Escalated", "Count": report.escalated_count},
        ]
    )
    return (
        alt.Chart(frame)
        .mark_arc(innerRadius=62, cornerRadius=4)
        .encode(
            theta="Count:Q",
            color=alt.Color(
                "Outcome:N",
                scale=alt.Scale(domain=["Auto-approved", "Escalated"], range=["#0E9F8E", "#F4A62A"]),
                legend=alt.Legend(orient="bottom", title=None),
            ),
            tooltip=["Outcome", "Count"],
        )
        .properties(height=300)
        .configure_view(strokeWidth=0)
    )


def render_sidebar_connection() -> None:
    st.markdown("## Co Audit")
    st.caption("Human-in-the-loop 10-K auditor")
    previous_mode = st.session_state.backend_mode
    st.session_state.backend_mode = st.radio(
        "Data backend",
        options=["Live FastAPI", "Sample Data"],
        index=0 if st.session_state.backend_mode == "Live FastAPI" else 1,
        horizontal=True,
    )
    if st.session_state.backend_mode != previous_mode:
        st.session_state.active_thread_id = None
        st.session_state.first_approvals = {}
    if st.session_state.backend_mode == "Live FastAPI":
        st.session_state.api_url = st.text_input("FastAPI URL", value=st.session_state.api_url)


def render_sidebar_controls(
    client: AuditClientProtocol, config: Config, active_run: Optional[RunState]
) -> Dict[str, object]:
    if active_run is None:
        if st.session_state.backend_mode == "Sample Data":
            st.markdown('<span class="badge badge-sample">Sample data</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge badge-live">FastAPI connected</span>', unsafe_allow_html=True)
    else:
        st.markdown(source_badge_html(active_run.data_source), unsafe_allow_html=True)

    st.markdown("---")
    ticker = st.selectbox(
        "Company filing",
        options=list(COMPANIES.keys()),
        format_func=lambda key: COMPANIES[key],
    )
    st.session_state.fault_switch = st.toggle("Fault switch (simulation)", value=st.session_state.fault_switch)
    run_clicked = st.button("Run audit", type="primary", **STRETCH)
    st.markdown(user_chip_html(st.session_state.reviewer_id, st.session_state.reviewer_role), unsafe_allow_html=True)
    if st.button("Switch reviewer", **STRETCH):
        st.session_state.signed_in = False
        st.rerun()

    st.markdown("---")
    st.markdown("### Escalation thresholds")
    new_confidence = st.slider(
        "Confidence threshold",
        min_value=0.50,
        max_value=0.99,
        value=float(config.confidence_threshold),
        step=0.01,
    )
    new_yoy = st.slider(
        "Year-on-year threshold",
        min_value=0.05,
        max_value=1.00,
        value=float(config.year_on_year_threshold),
        step=0.05,
    )
    updated_config = config
    changed = (
        abs(new_confidence - config.confidence_threshold) > 1e-6
        or abs(new_yoy - config.year_on_year_threshold) > 1e-6
    )
    if changed:
        try:
            updated_config = client.update_config(
                Config(
                    confidence_threshold=new_confidence,
                    year_on_year_threshold=new_yoy,
                    equation_tolerance=config.equation_tolerance,
                    spot_check_rate=config.spot_check_rate,
                )
            )
            st.toast("Thresholds saved.")
        except Exception as error:
            st.error(f"Could not update thresholds: {error}")
    return {"ticker": ticker, "run_clicked": run_clicked, "config": updated_config}


def render_header(run: RunState) -> None:
    workflow_badge = (
        '<span class="badge badge-status-paused">Paused for review</span>'
        if run.workflow_status == "PAUSED_FOR_REVIEW"
        else '<span class="badge badge-status-completed">Workflow completed</span>'
    )
    period = run.metrics[0].period_end if run.metrics else "n/a"
    st.markdown(
        '<div class="top-header">'
        f"<div><h1>{html.escape(display_company(run.company_name))} ({html.escape(run.ticker)})</h1>"
        f'<p class="subtitle">Thread {html.escape(run.thread_id)} &middot; Period end {html.escape(period)}</p></div>'
        f"<div>{source_badge_html(run.data_source)} {workflow_badge} "
        f"{user_chip_html(st.session_state.reviewer_id, st.session_state.reviewer_role, compact=True)}</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(pipeline_stepper_html(run.workflow_status), unsafe_allow_html=True)


def render_kpis(run: RunState, report: Optional[ReportResponse]) -> None:
    columns = st.columns(5)
    report_ready = report is not None and len(report.per_metric_accuracy) > 0
    if not report_ready:
        flagged = sum(1 for m in run.metrics if m.status == "FLAGGED")
        approved = sum(1 for m in run.metrics if m.status == "APPROVED")
        values = [
            ("Extraction accuracy", "Pending", "Ready after the review"),
            ("Escalation precision", "Pending", "Ready after the review"),
            ("Auto-approved", str(approved), "No human needed"),
            ("Escalated", str(flagged), "Waiting for a reviewer"),
            ("Est. time saved", f"{approved * 12}m", "Estimate: 12 min per value"),
        ]
    else:
        values = [
            ("Extraction accuracy", f"{report.extraction_accuracy_pct:.1f}%", "Against SEC XBRL data"),
            ("Escalation precision", f"{report.escalation_precision_pct:.1f}%", "Flags that were real errors"),
            ("Auto-approved", str(report.auto_approved_count), "No human needed"),
            ("Escalated", str(report.escalated_count), "Sent to a reviewer"),
            ("Est. time saved", f"{report.auto_approved_count * 12}m", "Estimate: 12 min per value"),
        ]
    for column, (label, value, hint) in zip(columns, values):
        with column:
            st.markdown(kpi_html(label, value, hint), unsafe_allow_html=True)


def render_overview(run: RunState, config: Config) -> None:
    st.markdown(metrics_table_html(run, config), unsafe_allow_html=True)
    st.markdown("#### Validation checks")
    st.markdown(validation_list_html(run.validations), unsafe_allow_html=True)

def record_decision(
    client: AuditClientProtocol,
    item_id: str,
    metric_name: str,
    action: str,
    corrected_value: Optional[float],
    notes: str,
    reviewer: str,
    success_message: str,
) -> None:
    with st.spinner("Recording decision..."):
        try:
            client.submit_decision(
                review_id=item_id,
                action=action,
                corrected_value=corrected_value,
                notes=notes,
                reviewer_id=reviewer,
            )
            st.session_state.first_approvals.pop(item_id, None)
            st.session_state.flash_message = success_message
            st.rerun()
        except Exception as error:
            st.error(f"Decision failed: {error}")


def render_review_card(
    client: AuditClientProtocol,
    run: RunState,
    config: Config,
    item,
    rank: int,
    metric: ExtractedMetric,
) -> None:
    exposure = materiality_score(metric, run.validations)
    requires_dual = abs(metric.value) >= TWO_PERSON_LIMIT_USD
    first_reviewer = st.session_state.first_approvals.get(item.id)

    with st.container(border=True):
        left, right = st.columns([3, 2], gap="large")
        with left:
            st.markdown(
                f'<p class="review-title">#{rank} &middot; {html.escape(display_name(item.metric))} &mdash; {format_usd(metric.value)}</p>'
                f'<p class="review-reason">{html.escape(item.reason)}</p>',
                unsafe_allow_html=True,
            )
            if requires_dual:
                if first_reviewer:
                    st.warning(
                        f"Two-person approval: first sign-off by '{first_reviewer}'. A different reviewer ID must finish."
                    )
                else:
                    st.info(f"Values of {format_usd(TWO_PERSON_LIMIT_USD)} or more need two different reviewer IDs.")
            st.markdown(metric_checks_html(item.metric, run.validations), unsafe_allow_html=True)
            st.markdown(
                '<div class="source-box">'
                f"<strong>Source ({html.escape(metric.source_location)}):</strong><br>{html.escape(metric.source_snippet)}"
                "</div>",
                unsafe_allow_html=True,
            )
            with st.expander("Click-to-source: see the filing table", expanded=(rank == 1)):
                st.markdown(click_to_source_html(run, item.metric), unsafe_allow_html=True)
        with right:
            st.markdown(confidence_ring_html(metric.confidence, config.confidence_threshold), unsafe_allow_html=True)
            st.markdown(
                f'<div class="stat-row"><span>Confidence</span><span>{metric.confidence:.2f} / {config.confidence_threshold:.2f}</span></div>'
                f'<div class="stat-row"><span>Risk exposure</span><span>{format_usd(exposure)}</span></div>'
                f'<div class="stat-row"><span>Extractor</span><span>{html.escape(metric.extractor.upper())}</span></div>'
                f'<div class="stat-row"><span>Period</span><span>{html.escape(metric.fiscal_label)}</span></div>',
                unsafe_allow_html=True,
            )
            notes = st.text_input("Reviewer notes", key=f"notes_{item.id}", placeholder="Why you decided this")
            corrected_raw = st.text_input(
                "Corrected value (USD)",
                key=f"corr_{item.id}",
                placeholder=f"For example {int(metric.value)}",
            )
            approve_col, edit_col, reject_col = st.columns(3)
            reviewer = st.session_state.reviewer_id.strip()

            with approve_col:
                approve = st.button("Approve", key=f"app_{item.id}", type="primary", **STRETCH)
            with edit_col:
                edit = st.button("Edit", key=f"edt_{item.id}", **STRETCH)
            with reject_col:
                reject = st.button("Reject", key=f"rej_{item.id}", **STRETCH)

            if approve:
                if not reviewer:
                    st.error("Enter a reviewer ID in the sidebar first.")
                elif requires_dual and not first_reviewer:
                    st.session_state.first_approvals[item.id] = reviewer
                    st.session_state.flash_message = (
                        f"First approval by {reviewer} for {item.metric}. Switch the reviewer ID for the second sign-off."
                    )
                    st.rerun()
                elif requires_dual and first_reviewer == reviewer:
                    st.error(f"'{reviewer}' already gave the first sign-off. Use a different reviewer ID.")
                else:
                    combined = (
                        f"[Co-approved: {first_reviewer} and {reviewer}] {notes}".strip() if first_reviewer else notes
                    )
                    record_decision(client, item.id, item.metric, "APPROVED", None, combined, reviewer, f"Approved {item.metric}.")
            if edit:
                parsed = parse_numeric_input(corrected_raw)
                if parsed is None:
                    st.error("The corrected value must be a valid number.")
                elif not reviewer:
                    st.error("Enter a reviewer ID in the sidebar first.")
                else:
                    record_decision(
                        client, item.id, item.metric, "CORRECTED", parsed, notes, reviewer,
                        f"Corrected {item.metric} to {format_usd(parsed)}.",
                    )
            if reject:
                if not reviewer:
                    st.error("Enter a reviewer ID in the sidebar first.")
                else:
                    record_decision(client, item.id, item.metric, "REJECTED", None, notes, reviewer, f"Rejected {item.metric}.")


def render_review_queue(client: AuditClientProtocol, run: RunState, config: Config) -> None:
    try:
        pending = client.list_reviews(status="PENDING", thread_id=run.thread_id)
        done = client.list_reviews(status="DONE", thread_id=run.thread_id)
    except Exception as error:
        st.error(f"Could not load the review queue: {error}")
        return

    lookup: Dict[str, ExtractedMetric] = {m.metric_name: m for m in run.metrics}
    pending.sort(key=lambda r: materiality_score(lookup[r.metric], run.validations), reverse=True)

    pending_tab, done_tab = st.tabs([f"Pending ({len(pending)})", f"Completed ({len(done)})"])
    with pending_tab:
        if not pending:
            st.success("All flagged values have been reviewed. The workflow has resumed and finished.")
        else:
            st.caption("Sorted by risk exposure: the biggest potential mistake comes first.")
            for rank, item in enumerate(pending, start=1):
                render_review_card(client, run, config, item, rank, lookup[item.metric])
    with done_tab:
        if not done:
            st.info("No completed reviews for this run yet.")
        for item in done:
            metric = lookup[item.metric]
            st.markdown(
                '<div class="section-card">'
                f"{status_pill_html(metric.status)} <strong>{html.escape(display_name(item.metric))}</strong> &mdash; "
                f"final value <strong>{format_usd(metric.value)}</strong><br>"
                f"<small>Flagged for: {html.escape(item.reason)} &middot; {html.escape(item.created_at)}</small>"
                "</div>",
                unsafe_allow_html=True,
            )


def render_scorecard(run: RunState, config: Config, report: Optional[ReportResponse]) -> None:
    if report is None:
        st.info("The accuracy report is not ready yet.")
        return
    donut_col, left = st.columns([1, 2], gap="large")
    with donut_col:
        st.markdown("#### How values were handled")
        st.caption("Auto-approved by the agent, or escalated to a human.")
        st.altair_chart(handling_chart(report), **STRETCH)
    has_differences = any(row.error_pct >= 0.01 for row in report.per_metric_accuracy)
    with left:
        st.markdown("#### Escalation curve")
        st.caption("Each point is a confidence threshold. The amber marker is your current setting. The dashed line is random review.")
        st.altair_chart(escalation_chart(build_escalation_points(run, report), config.confidence_threshold), **STRETCH)
        if not has_differences:
            st.caption("This run has no real errors, so every threshold catches 100%. Turn on the fault switch to see the curve bend.")
    right = st.container()
    with right:
        st.markdown("#### Accuracy against SEC XBRL data")
        if has_differences:
            st.caption("Bars show how far each final value is from the SEC's official number.")
            st.altair_chart(accuracy_chart(report), **STRETCH)
        else:
            matched = len(report.per_metric_accuracy)
            pills = "".join(
                f'<span class="pill pill-approved" style="margin:0 0.35rem 0.4rem 0;">{html.escape(row.metric_name)}</span>'
                for row in report.per_metric_accuracy
            )
            st.markdown(
                '<div class="section-card">'
                f'<p class="review-title">All {matched} values match the SEC data</p>'
                '<p class="review-reason">Every final value equals the official XBRL number.</p>'
                f"{pills}</div>",
                unsafe_allow_html=True,
            )

    st.markdown("#### Per-metric detail")
    frame = pd.DataFrame(
        [
            {
                "Metric": display_name(row.metric_name),
                "Final value": format_usd(row.extracted_value),
                "SEC XBRL value": format_usd(row.ground_truth_value),
                "Difference": f"{row.error_pct:.2f}%",
                "Match": "Yes" if row.accurate else "No",
            }
            for row in report.per_metric_accuracy
        ]
    )
    st.dataframe(frame, hide_index=True, **STRETCH)


def render_audit_log(client: AuditClientProtocol, run: RunState, report: Optional[ReportResponse]) -> None:
    try:
        entries = client.get_audit_log()
    except Exception as error:
        st.error(f"Could not load the audit log: {error}")
        return
    st.caption("Append-only: new decisions are added as rows. Nothing is edited or deleted.")
    if not entries:
        st.info("No human decisions yet. Approve, edit or reject a flagged value to add a row.")
    else:
        frame = pd.DataFrame(
            [
                {
                    "Audit ID": e.audit_id,
                    "Time": e.timestamp,
                    "Company": e.company,
                    "Metric": display_name(e.metric),
                    "Original": format_usd(e.original_value),
                    "Final": format_usd(e.final_value),
                    "Decision": e.decision,
                    "Reviewer": e.reviewer_id,
                    "Notes": e.reviewer_notes or "-",
                    "Simulated": "Yes" if e.simulated else "No",
                }
                for e in entries
            ]
        )
        st.dataframe(frame, hide_index=True, **STRETCH)
    if report is not None:
        first, second = st.columns(2)
        with first:
            st.download_button(
                "Export workpaper (CSV)",
                data=build_workpaper_csv(run, report, entries),
                file_name=f"co_audit_{run.ticker.lower()}_{run.thread_id}.csv",
                mime="text/csv",
                **STRETCH,
            )
        with second:
            st.download_button(
                "Export workpaper (HTML)",
                data=build_workpaper_html(run, report, entries),
                file_name=f"co_audit_{run.ticker.lower()}_{run.thread_id}.html",
                mime="text/html",
                **STRETCH,
            )


def render_home(config: Config) -> None:
    name = html.escape(st.session_state.reviewer_id)
    mode = "Sample data" if st.session_state.backend_mode == "Sample Data" else "Live FastAPI"
    st.markdown(
        '<div class="top-header"><div>'
        f"<h1>Welcome, {name}</h1>"
        '<p class="subtitle">Choose a filing to audit. Anything the agent is unsure about will wait for you.</p></div>'
        f"<div>{user_chip_html(st.session_state.reviewer_id, st.session_state.reviewer_role, compact=True)}</div></div>",
        unsafe_allow_html=True,
    )
    summary = [
        ("Data backend", mode, "Switch it in the sidebar"),
        ("Confidence threshold", f"{config.confidence_threshold:.2f}", "Below this, a human reviews"),
        ("Year-on-year threshold", f"{config.year_on_year_threshold:.0%}", "Bigger changes are flagged"),
        ("Spot-check rate", f"{config.spot_check_rate:.0%}", "Share of approvals re-checked"),
    ]
    for column, (label, value, hint) in zip(st.columns(4), summary):
        with column:
            st.markdown(kpi_html(label, value, hint), unsafe_allow_html=True)
    st.markdown("#### Choose a filing to audit")
    tickers = list(COMPANIES.keys())
    for start in range(0, len(tickers), 4):
        for column, ticker in zip(st.columns(4), tickers[start : start + 4]):
            with column:
                company_name = html.escape(COMPANIES[ticker].split(" (")[0])
                st.markdown(
                    f'<div class="company-card"><span class="company-ticker">{ticker}</span>'
                    f'<p class="company-name">{company_name}</p></div>',
                    unsafe_allow_html=True,
                )
                if st.button(f"Audit {ticker}", key=f"audit_{ticker}", **STRETCH):
                    st.session_state.requested_ticker = ticker
                    st.rerun()


def main() -> None:
    st.set_page_config(page_title="Co Audit | Reviewer Dashboard", layout="wide")
    apply_custom_styles()
    init_state()

    if not st.session_state.signed_in:
        render_login(STRETCH)
        return

    with st.sidebar:
        render_sidebar_connection()

    client = get_active_client()
    try:
        config = client.get_config()
    except Exception as error:
        st.error(
            f"Cannot reach the backend at {st.session_state.api_url} ({error}). "
            "Check that uvicorn is running, or switch the data backend to Sample Data."
        )
        return

    active_run: Optional[RunState] = None
    if st.session_state.active_thread_id:
        try:
            active_run = client.get_run(st.session_state.active_thread_id)
        except Exception as error:
            st.error(f"Could not load run {st.session_state.active_thread_id}: {error}")
            st.session_state.active_thread_id = None

    with st.sidebar:
        controls = render_sidebar_controls(client, config, active_run)
    config = controls["config"]

    banner_slot = st.empty()
    flash_slot = st.empty()
    if active_run and active_run.fault_injected:
        banner_slot.markdown(
            '<div class="fault-banner">Fault injected (simulation): a value was corrupted before validation. The backend checks must catch it.</div>',
            unsafe_allow_html=True,
        )
    elif st.session_state.fault_switch:
        banner_slot.markdown(
            '<div class="fault-banner">Fault switch is armed (simulation): the next audit will corrupt one value so the backend checks can be shown catching it.</div>',
            unsafe_allow_html=True,
        )

    ticker_to_run = controls["ticker"] if controls["run_clicked"] else st.session_state.requested_ticker
    st.session_state.requested_ticker = None
    if ticker_to_run:
        with st.spinner(f"Running the audit for {ticker_to_run}..."):
            try:
                thread_id = client.start_run(ticker=ticker_to_run, fault_switch=st.session_state.fault_switch)
                st.session_state.active_thread_id = thread_id
                st.session_state.flash_message = f"Audit started for {ticker_to_run}."
                st.rerun()
            except Exception as error:
                st.error(f"Could not start the audit: {error}")

    if st.session_state.flash_message:
        flash_slot.success(st.session_state.flash_message)
        st.session_state.flash_message = None

    if active_run is None:
        render_home(config)
        return

    report = load_report(client, active_run.thread_id)
    render_header(active_run)
    if active_run.workflow_status == "COMPLETED":
        st.markdown(
            '<div class="completion-card"><strong>Audit complete.</strong> Every flagged value has been reviewed, '
            "the workflow has resumed and finished, and each decision is in the append-only log.</div>",
            unsafe_allow_html=True,
        )
    render_kpis(active_run, report)

    try:
        pending_count = len(client.list_reviews(status="PENDING", thread_id=active_run.thread_id))
    except Exception:
        pending_count = 0

    overview_tab, review_tab, score_tab, audit_tab = st.tabs(
        ["Overview", f"Review queue ({pending_count})", "Scorecard", "Audit log"]
    )
    with overview_tab:
        render_overview(active_run, config)
    with review_tab:
        render_review_queue(client, active_run, config)
    with score_tab:
        render_scorecard(active_run, config, report)
    with audit_tab:
        render_audit_log(client, active_run, report)


if __name__ == "__main__":
    main()

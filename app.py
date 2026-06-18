from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vat_reconciliation_engine.config_loader import load_config
from vat_reconciliation_engine.exporter import build_exception_workbook_bytes
from vat_reconciliation_engine.ingestion import (
    DATASET_LABELS,
    load_sample_data,
    load_uploaded_data,
    missing_upload_datasets,
    required_upload_datasets,
)
from vat_reconciliation_engine.reconciliation import build_reconciliation
from vat_reconciliation_engine.schema import SchemaValidationError

CONFIG_PATH = ROOT / "config" / "vat_generic.yml"
SAMPLE_DATA_PATH = ROOT / "data" / "sample"


def inject_dashboard_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #e5e7eb;
        }

        .hero-card {
            background: linear-gradient(135deg, #ffffff 0%, #eef5ff 100%);
            border: 1px solid #d9e4f5;
            border-radius: 14px;
            padding: 1.35rem 1.5rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
        }

        .hero-title {
            color: #172033;
            font-size: 2.2rem;
            font-weight: 760;
            margin: 0;
            line-height: 1.12;
        }

        .hero-copy {
            color: #3f4b5f;
            font-size: 1rem;
            line-height: 1.55;
            max-width: 58rem;
            margin: 0.75rem 0 0;
        }

        .section-header {
            border-left: 4px solid #2563eb;
            padding: 0.15rem 0 0.15rem 0.75rem;
            margin: 1.35rem 0 0.75rem;
        }

        .section-header h2 {
            color: #172033;
            font-size: 1.18rem;
            font-weight: 720;
            margin: 0;
        }

        .section-header p {
            color: #64748b;
            margin: 0.18rem 0 0;
            font-size: 0.92rem;
        }

        .metric-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1rem 1.05rem;
            min-height: 8.2rem;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.045);
        }

        .metric-label {
            color: #64748b;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }

        .metric-value {
            color: #172033;
            font-size: 1.65rem;
            font-weight: 760;
            margin-bottom: 0.4rem;
        }

        .metric-caption {
            color: #64748b;
            font-size: 0.86rem;
            line-height: 1.35;
        }

        .status-pill {
            display: inline-block;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 720;
            padding: 0.2rem 0.55rem;
            margin-bottom: 0.35rem;
        }

        .status-pass {
            background: #dcfce7;
            color: #166534;
            border: 1px solid #bbf7d0;
        }

        .status-review {
            background: #fef3c7;
            color: #92400e;
            border: 1px solid #fde68a;
        }

        .status-risk {
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #fecaca;
        }

        .review-note {
            background: #ffffff;
            border: 1px solid #dbeafe;
            border-left: 4px solid #2563eb;
            border-radius: 10px;
            color: #334155;
            padding: 0.95rem 1rem;
            margin: 0.5rem 0 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <h1 class="hero-title">VAT Reconciliation Engine</h1>
            <p class="hero-copy">
                Review VAT source registers, VAT return summary boxes, VAT
                payment/refund context, and GL VAT control account movement in
                one deterministic workflow. The dashboard highlights return
                variances, control account differences, documentation
                exceptions, and audit-ready workbook evidence for follow-up.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, caption: str) -> None:
    st.markdown(
        f"""
        <div class="section-header">
            <h2>{title}</h2>
            <p>{caption}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def variance_status(value: float) -> tuple[str, str]:
    if abs(value) <= 0.01:
        return "Pass", "pass"
    return "Review needed", "review"


def exception_status(count: int) -> tuple[str, str]:
    if count == 0:
        return "Pass", "pass"
    return "Control risk", "risk"


def render_status_card(label: str, value: str, caption: str, status: str, tone: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="status-pill status-{tone}">{status}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="VAT Reconciliation Engine", layout="wide")
inject_dashboard_css()
render_hero()

config = load_config(CONFIG_PATH)

with st.sidebar:
    st.header("Data Mode")
    data_mode = st.radio(
        "Choose review dataset",
        ["Use bundled demo data", "Upload my own CSV exports"],
        label_visibility="collapsed",
    )

    uploaded_files = {}
    if data_mode == "Upload my own CSV exports":
        st.caption("Upload all five required CSV exports. Files are processed in-session only.")
        for dataset in required_upload_datasets():
            uploaded_files[dataset] = st.file_uploader(
                DATASET_LABELS[dataset],
                type=["csv"],
                key=f"upload_{dataset}",
            )

missing_uploads = missing_upload_datasets(uploaded_files)
if data_mode == "Upload my own CSV exports" and missing_uploads:
    missing_labels = [DATASET_LABELS[dataset] for dataset in missing_uploads]
    with st.sidebar:
        st.warning("Upload mode needs all five CSV files before reconciliation can run.")
    st.info(
        "Upload all required CSV exports to run the VAT reconciliation. Missing files: "
        + ", ".join(missing_labels)
        + "."
    )
    st.stop()

try:
    if data_mode == "Upload my own CSV exports":
        data = load_uploaded_data(uploaded_files, config)
        data_source = "Uploaded CSV exports"
    else:
        data = load_sample_data(SAMPLE_DATA_PATH, config)
        data_source = "`data/sample/` bundled demo CSVs"
except SchemaValidationError as exc:
    st.error(f"Schema validation failed: {exc}")
    st.info("Check the uploaded CSV column names against `config/vat_generic.yml`.")
    st.stop()
except Exception as exc:  # noqa: BLE001
    st.error(f"Unable to read uploaded CSV files: {exc}")
    st.info("Confirm each upload is a valid CSV file with the documented columns.")
    st.stop()

result = build_reconciliation(data, config)

with st.sidebar:
    st.header("Review Context")
    st.write("Current release: v0.1.3")
    st.write(f"Mode: {data_mode}")
    st.write(f"Data source: {data_source}")
    st.write("Config: `config/vat_generic.yml`")
    st.caption(
        "The public repo ships with demo data. Uploaded files are processed for "
        "the current Streamlit session and are not persisted by the app."
    )

render_section_header(
    "How To Read This Dashboard",
    "A short review path for VAT return sign-off and control follow-up.",
)
st.markdown(
    """
    Start with the variance metrics, then review the reconciliation table to see
    which control check produced the difference. Use the exception table for
    transaction-level follow-up, and expand the source registers when you need
    to trace a dashboard result back to the underlying CSV rows.
    """
)

summary = result.summary
exception_count = len(result.exceptions)
output_status, output_tone = variance_status(summary.output_vat_variance)
input_status, input_tone = variance_status(summary.input_vat_variance)
gl_status, gl_tone = variance_status(summary.gl_control_variance)
exceptions_status, exceptions_tone = exception_status(exception_count)

render_section_header(
    "VAT Position Summary",
    "Status cards show whether each finance-control check passes or needs review.",
)
metric_cols = st.columns(4)
with metric_cols[0]:
    render_status_card(
        "Output VAT return variance",
        f"{summary.output_vat_variance:,.2f}",
        "Sales-register VAT less VAT return output amount.",
        output_status,
        output_tone,
    )
with metric_cols[1]:
    render_status_card(
        "Input VAT claim variance",
        f"{summary.input_vat_variance:,.2f}",
        "Claimed purchase VAT less VAT return input amount.",
        input_status,
        input_tone,
    )
with metric_cols[2]:
    render_status_card(
        "VAT GL control variance",
        f"{summary.gl_control_variance:,.2f}",
        "Expected VAT control balance compared to GL movement.",
        gl_status,
        gl_tone,
    )
with metric_cols[3]:
    render_status_card(
        "Open review exceptions",
        str(exception_count),
        "Documentation, duplicate, unclaimed VAT, and control exceptions.",
        exceptions_status,
        exceptions_tone,
    )

if exception_count:
    st.warning(f"{exception_count} exceptions need review before sign-off.")
else:
    st.success("No exceptions were identified for the selected dataset.")

render_section_header(
    "Reconciliation Checks",
    "Three core checks compare source-register calculations to the VAT return "
    "summary and GL VAT control account movement.",
)
st.dataframe(pd.DataFrame(result.return_reconciliation), use_container_width=True)

render_section_header(
    "Exception Register",
    "Each exception identifies a control or documentation issue that needs "
    "review before the VAT position is finalized.",
)
st.dataframe(result.exceptions, use_container_width=True)

render_section_header(
    "Source Data Review",
    "Expand source inputs to trace dashboard results back to CSV rows.",
)
with st.expander("Source Registers And Return Inputs"):
    st.write("Sales VAT Register")
    st.dataframe(data.sales, use_container_width=True)
    st.write("Purchase VAT Register")
    st.dataframe(data.purchases, use_container_width=True)
    st.write("VAT Return Summary")
    st.dataframe(data.vat_return, use_container_width=True)
    st.write("VAT GL Control")
    st.dataframe(data.gl, use_container_width=True)
    st.write("VAT Payments And Refunds")
    st.dataframe(data.payments_refunds, use_container_width=True)

render_section_header(
    "Export Workbook",
    "Download an audit-ready Excel exception workbook for the current dashboard dataset.",
)
workbook_bytes = build_exception_workbook_bytes(data, result)
st.markdown(
    """
    <div class="review-note">
        The workbook includes summary, source detail, exceptions, and
        reconciling items for the dataset currently loaded in the dashboard.
    </div>
    """,
    unsafe_allow_html=True,
)
st.download_button(
    "Download VAT exception workbook",
    data=workbook_bytes,
    file_name="vat_exception_workbook.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

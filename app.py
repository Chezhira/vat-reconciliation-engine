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


st.set_page_config(page_title="VAT Reconciliation Engine", layout="wide")

st.title("VAT Reconciliation Engine")
st.caption("VAT return review, GL control account reconciliation, and exception reporting.")

st.markdown(
    """
    Review VAT source registers, VAT return summary boxes, VAT payment/refund
    context, and GL VAT control account movement in one deterministic dashboard.
    The review path highlights return variances, control account differences,
    documentation gaps, and the audit-ready workbook generated for follow-up.
    """
)

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
    st.write("Current release: v0.1.2")
    st.write(f"Mode: {data_mode}")
    st.write(f"Data source: {data_source}")
    st.write("Config: `config/vat_generic.yml`")
    st.caption(
        "The public repo ships with demo data. Uploaded files are processed for "
        "the current Streamlit session and are not persisted by the app."
    )

st.subheader("How To Read This Dashboard")
st.markdown(
    """
    Start with the variance metrics, then review the reconciliation table to see
    which control check produced the difference. Use the exception table for
    transaction-level follow-up, and expand the source registers when you need
    to trace a dashboard result back to the underlying CSV rows.
    """
)

summary = result.summary
metric_cols = st.columns(4)
metric_cols[0].metric("Output VAT return variance", f"{summary.output_vat_variance:,.2f}")
metric_cols[1].metric("Input VAT claim variance", f"{summary.input_vat_variance:,.2f}")
metric_cols[2].metric("VAT GL control variance", f"{summary.gl_control_variance:,.2f}")
metric_cols[3].metric("Open review exceptions", str(len(result.exceptions)))

st.subheader("VAT Return And GL Reconciliation")
st.caption(
    "Three core checks compare source-register calculations to the VAT return "
    "summary and GL VAT control account movement."
)
st.dataframe(pd.DataFrame(result.return_reconciliation), use_container_width=True)

st.subheader("Exception Review")
st.caption(
    "Each exception identifies a control or documentation issue that needs "
    "review before the VAT position is finalized."
)
st.dataframe(result.exceptions, use_container_width=True)

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

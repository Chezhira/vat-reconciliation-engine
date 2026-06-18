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
from vat_reconciliation_engine.ingestion import load_sample_data
from vat_reconciliation_engine.reconciliation import build_reconciliation


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

config = load_config(ROOT / "config" / "vat_generic.yml")
data = load_sample_data(ROOT / "data" / "sample", config)
result = build_reconciliation(data, config)

with st.sidebar:
    st.header("Review Context")
    st.write("Current release: v0.1.2")
    st.write("Mode: public portfolio demo")
    st.write("Data source: `data/sample/` CSV exports")
    st.write("Config: `config/vat_generic.yml`")
    st.caption(
        "The public repo ships with demo data. Users can replace the CSV files "
        "with exports that follow the documented schema."
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

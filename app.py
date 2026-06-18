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
st.caption("Synthetic portfolio MVP. Deterministic reconciliation only.")

config = load_config(ROOT / "config" / "vat_generic.yml")
data = load_sample_data(ROOT / "data" / "sample", config)
result = build_reconciliation(data, config)

summary = result.summary
metric_cols = st.columns(4)
metric_cols[0].metric("Output VAT variance", f"{summary.output_vat_variance:,.2f}")
metric_cols[1].metric("Input VAT variance", f"{summary.input_vat_variance:,.2f}")
metric_cols[2].metric("GL control variance", f"{summary.gl_control_variance:,.2f}")
metric_cols[3].metric("Exceptions", str(len(result.exceptions)))

st.subheader("VAT Return Reconciliation")
st.dataframe(pd.DataFrame(result.return_reconciliation), use_container_width=True)

st.subheader("Exceptions")
st.dataframe(result.exceptions, use_container_width=True)

with st.expander("Synthetic Source Registers"):
    st.write("Sales VAT Register")
    st.dataframe(data.sales, use_container_width=True)
    st.write("Purchase VAT Register")
    st.dataframe(data.purchases, use_container_width=True)
    st.write("VAT GL Control")
    st.dataframe(data.gl, use_container_width=True)

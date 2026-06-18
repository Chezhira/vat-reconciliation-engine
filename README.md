# VAT Reconciliation Engine

Synthetic-data-only Finance Engineer portfolio MVP for reconciling VAT source
registers to a VAT return summary and VAT GL control account.

## Scope

- Synthetic sample CSVs only.
- Deterministic pandas reconciliation logic.
- Config-first VAT rates, thresholds, mandatory fields, and return box mapping.
- Streamlit dashboard for reviewing the VAT position.
- Excel exception workbook for audit-ready review.

No LLM calls, OCR, APIs, authentication, databases, live integrations, or tax
authority connections are included in this MVP.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe scripts\run_sample_smoke.py
.\.venv\Scripts\python.exe -m pytest -q
streamlit run app.py
```

The smoke test writes a sample exception workbook to
`outputs/sample_vat_recon/sample_vat_exception_workbook.xlsx`.

# VAT Reconciliation Engine

Synthetic-data-only Finance Engineer portfolio MVP for reconciling VAT source
registers to a VAT return summary and VAT GL control account, then exporting an
audit-ready exception workbook.

## What It Does

The VAT Reconciliation Engine ingests bundled synthetic CSV files, validates
their configured schemas, runs deterministic VAT reconciliation checks, and
writes a sample Excel workbook for review. The Streamlit dashboard gives a quick
view of the VAT position, return variances, GL control variance, source
registers, and exception list.

This is a finance-control vertical slice rather than a tax filing system. It
shows how a Finance Engineer can turn messy VAT review work into a repeatable
control layer: configured inputs, deterministic checks, exception evidence, and
an export that supports audit follow-up.

## Scope

- Synthetic sample CSVs only.
- Deterministic pandas reconciliation logic.
- Config-first VAT rates, thresholds, mandatory fields, and return box mapping.
- Streamlit dashboard for reviewing the VAT position.
- Excel exception workbook for audit-ready review.

No LLM calls, OCR, APIs, authentication, databases, live integrations, or tax
authority connections are included in this MVP.

## Inputs

The MVP reads these files from `data/sample/`:

- `sample_sales_vat_register.csv`
- `sample_purchase_vat_register.csv`
- `sample_vat_return.csv`
- `sample_gl_vat_control.csv`
- `sample_vat_payments_refunds.csv`

Validation rules, mandatory fields, VAT rates, materiality thresholds, and VAT
return box mappings are configured in `config/vat_generic.yml`.

## MVP Reconciliation Checks

The first vertical slice runs three core checks:

- VAT return output mismatch: compares output VAT in the sales register to the
  configured VAT return output box.
- VAT return input mismatch: compares claimed input VAT in the purchase register
  to the configured VAT return input box.
- GL control account variance: compares the expected VAT control balance to the
  VAT GL control account movement.

## Current Sample Exceptions

The bundled synthetic dataset currently produces six exceptions:

- Missing tax invoice reference: `SINV-1004`, sales, `504.00`.
- Missing supplier VAT number: `PINV-2003`, purchases, `162.00`.
- Duplicate invoice number: `SINV-1002`, sales, `1,350.00`.
- Duplicate invoice number: `SINV-1002`, sales, `216.00`.
- Unclaimed input VAT: `PINV-2005`, purchases, `270.00`.
- GL control account variance: reconciliation variance, `12.00`.

## Demo Walkthrough

For a reviewer-oriented walkthrough of the synthetic inputs, reconciliation
flow, sample exceptions, exported workbook, and Streamlit dashboard review path,
see [docs/demo_notes.md](docs/demo_notes.md).

## Run Locally

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Run tests:

```powershell
python -m pytest -q
```

Run the sample-data smoke script:

```powershell
python scripts\run_sample_smoke.py
```

Run the Streamlit dashboard:

```powershell
streamlit run app.py
```

Full local verification:

```powershell
python -m ruff check .
python -m ruff format --check .
python -m pytest -q
python scripts\run_sample_smoke.py
```

The smoke test writes a sample exception workbook to
`outputs/sample_vat_recon/sample_vat_exception_workbook.xlsx`.

## CI

GitHub Actions runs the same deterministic quality gates on push and pull
request:

```powershell
python -m ruff check .
python -m ruff format --check .
python -m pytest -q
python scripts\run_sample_smoke.py
```

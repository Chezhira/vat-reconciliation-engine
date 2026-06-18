# Demo Notes

These notes support the portfolio walkthrough for the VAT Reconciliation
Engine. The public repository uses a bundled synthetic dataset and does not
connect to tax authority, banking, payroll, supplier, OCR, LLM, API,
authentication, or database systems.

## What The App Demonstrates

The app demonstrates a deterministic VAT control workflow: source register
ingestion, schema validation, VAT return review, VAT GL control account
comparison, payment/refund context, exception identification, dashboard review,
and Excel workbook export.

It is designed as a portfolio-ready finance engineering slice. The point is to
show how repeatable control evidence can be produced from structured finance
data before any wider automation, integration, or filing workflow is considered.

## Synthetic Input Files

The demo reads five bundled CSV files from `data/sample/`:

- `sample_sales_vat_register.csv`: synthetic output VAT source transactions.
- `sample_purchase_vat_register.csv`: synthetic input VAT source transactions.
- `sample_vat_return.csv`: synthetic VAT return summary boxes.
- `sample_gl_vat_control.csv`: synthetic VAT control account movement.
- `sample_vat_payments_refunds.csv`: synthetic payment/refund activity.

The config file `config/vat_generic.yml` defines mandatory fields, VAT rates,
materiality thresholds, and VAT return box mappings.

## Reconciliation Flow

The current MVP flow is intentionally narrow:

1. Load synthetic source files.
2. Validate each file against the configured mandatory fields.
3. Calculate output VAT from the sales register.
4. Calculate claimed input VAT from the purchase register.
5. Compare calculated VAT values to the configured VAT return boxes.
6. Compare the expected VAT control balance to GL movement.
7. Produce an exception list and export the audit workbook.

## Six Current Sample Exceptions

The bundled sample data currently produces these six exceptions:

- Missing tax invoice reference: `SINV-1004`, sales, `504.00`.
- Missing supplier VAT number: `PINV-2003`, purchases, `162.00`.
- Duplicate invoice number: `SINV-1002`, sales, `1,350.00`.
- Duplicate invoice number: `SINV-1002`, sales, `216.00`.
- Unclaimed input VAT: `PINV-2005`, purchases, `270.00`.
- GL control account variance: reconciliation variance, `12.00`.

## Exported Workbook Review

The smoke script writes
`outputs/sample_vat_recon/sample_vat_exception_workbook.xlsx`.

Reviewers should use the workbook as audit evidence for the demo scenario:

- `summary`: high-level calculated VAT position and variances.
- `output_vat`: sales register detail supporting output VAT.
- `input_vat`: purchase register detail supporting input VAT.
- `gl_movement`: VAT control account movement.
- `payments_refunds`: payment/refund activity.
- `exceptions`: current exception list with source, reference, amount, and detail.
- `reconciling_items`: the three core reconciliation checks and their variances.

## Streamlit Dashboard Review

In the Streamlit dashboard, reviewers should look at:

- The metric row for output VAT variance, input VAT variance, GL control
  variance, and exception count.
- The VAT return reconciliation table for the three MVP checks.
- The exceptions table for transaction-level follow-up evidence.
- The synthetic source register expander to trace dashboard results back to
  source rows.

The dashboard is intentionally read-only and deterministic for the MVP.

## Screenshot Walkthrough

The screenshots in `docs/screenshots/` show the main finance-review path:

- [Dashboard summary](screenshots/vat_dashboard_summary.png): VAT position
  status cards and exception count for review triage.
- [Reconciliation checks](screenshots/vat_reconciliation_checks.png): the three
  core VAT return and GL control checks.
- [Exception register](screenshots/vat_exception_register.png):
  transaction-level documentation and control exceptions.
- [Upload mode](screenshots/vat_upload_mode.png): CSV upload controls for files
  that follow the documented schemas.
- [Workbook download](screenshots/vat_workbook_download.png): export action for
  the audit-ready exception workbook.

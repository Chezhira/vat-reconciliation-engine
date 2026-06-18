from __future__ import annotations

import pandas as pd

from vat_reconciliation_engine.exceptions import exception_row


def find_data_quality_exceptions(data) -> list[dict]:
    rows: list[dict] = []

    missing_sales_refs = data.sales[data.sales["tax_invoice_ref"].isna()]
    for record in missing_sales_refs.to_dict("records"):
        rows.append(
            exception_row(
                "Missing tax invoice reference",
                "sales",
                record["invoice_id"],
                record["vat_amount"],
                "Sales VAT invoice has no tax invoice reference.",
            )
        )

    missing_supplier_vat = data.purchases[data.purchases["supplier_vat_number"].isna()]
    for record in missing_supplier_vat.to_dict("records"):
        rows.append(
            exception_row(
                "Missing supplier VAT number",
                "purchases",
                record["invoice_id"],
                record["vat_amount"],
                "Purchase VAT invoice has no supplier VAT number.",
            )
        )

    duplicate_sales = data.sales[data.sales.duplicated("invoice_id", keep=False)]
    for record in duplicate_sales.to_dict("records"):
        rows.append(
            exception_row(
                "Duplicate invoice number",
                "sales",
                record["invoice_id"],
                record["vat_amount"],
                "Sales invoice number appears more than once.",
            )
        )

    unclaimed_input = data.purchases[
        (data.purchases["vat_amount"] > 0)
        & (data.purchases["claimed_in_return"].astype(str).str.lower() != "true")
    ]
    for record in unclaimed_input.to_dict("records"):
        rows.append(
            exception_row(
                "Unclaimed input VAT",
                "purchases",
                record["invoice_id"],
                record["vat_amount"],
                "Recoverable VAT exists but is not claimed in the return sample.",
            )
        )

    return rows


def return_amount(vat_return: pd.DataFrame, box_code: str) -> float:
    matches = vat_return.loc[vat_return["box_code"] == box_code, "amount"]
    if matches.empty:
        return 0.0
    return float(matches.iloc[0])

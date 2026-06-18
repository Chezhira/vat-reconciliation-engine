from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from vat_reconciliation_engine.exceptions import as_exception_frame, exception_row
from vat_reconciliation_engine.vat_rules import find_data_quality_exceptions, return_amount


@dataclass(frozen=True)
class ReconciliationSummary:
    calculated_output_vat: float
    return_output_vat: float
    output_vat_variance: float
    calculated_input_vat: float
    return_input_vat: float
    input_vat_variance: float
    gl_control_balance: float
    expected_gl_balance: float
    gl_control_variance: float


@dataclass(frozen=True)
class ReconciliationResult:
    summary: ReconciliationSummary
    return_reconciliation: list[dict]
    exceptions: pd.DataFrame


def build_reconciliation(data, config: dict) -> ReconciliationResult:
    mapping = config["return_box_mapping"]
    threshold = float(config["thresholds"]["material_variance"])

    output_vat = float(data.sales["vat_amount"].sum())
    input_vat = float(
        data.purchases.loc[
            data.purchases["claimed_in_return"].astype(str).str.lower() == "true",
            "vat_amount",
        ].sum()
    )
    return_output_vat = return_amount(data.vat_return, mapping["output_vat"])
    return_input_vat = return_amount(data.vat_return, mapping["input_vat"])

    gl_balance = float(data.gl["credit"].sum() - data.gl["debit"].sum())
    expected_gl_balance = output_vat - input_vat

    summary = ReconciliationSummary(
        calculated_output_vat=round(output_vat, 2),
        return_output_vat=round(return_output_vat, 2),
        output_vat_variance=round(output_vat - return_output_vat, 2),
        calculated_input_vat=round(input_vat, 2),
        return_input_vat=round(return_input_vat, 2),
        input_vat_variance=round(input_vat - return_input_vat, 2),
        gl_control_balance=round(gl_balance, 2),
        expected_gl_balance=round(expected_gl_balance, 2),
        gl_control_variance=round(gl_balance - expected_gl_balance, 2),
    )

    return_reconciliation = [
        {
            "rule": "VAT return output mismatch",
            "source_amount": summary.calculated_output_vat,
            "return_amount": summary.return_output_vat,
            "variance": summary.output_vat_variance,
        },
        {
            "rule": "VAT return input mismatch",
            "source_amount": summary.calculated_input_vat,
            "return_amount": summary.return_input_vat,
            "variance": summary.input_vat_variance,
        },
        {
            "rule": "GL control account variance",
            "source_amount": summary.expected_gl_balance,
            "return_amount": summary.gl_control_balance,
            "variance": summary.gl_control_variance,
        },
    ]

    exception_rows = find_data_quality_exceptions(data)
    for item in return_reconciliation:
        if abs(float(item["variance"])) > threshold:
            exception_rows.append(
                exception_row(
                    item["rule"],
                    "reconciliation",
                    item["rule"],
                    item["variance"],
                    "Variance exceeds configured materiality threshold.",
                )
            )

    return ReconciliationResult(
        summary=summary,
        return_reconciliation=return_reconciliation,
        exceptions=as_exception_frame(exception_rows),
    )

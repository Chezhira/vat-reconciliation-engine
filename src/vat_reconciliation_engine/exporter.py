from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import pandas as pd


def export_exception_workbook(data, result, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    summary_df = pd.DataFrame([asdict(result.summary)])
    return_recon_df = pd.DataFrame(result.return_reconciliation)

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="summary", index=False)
        data.sales.to_excel(writer, sheet_name="output_vat", index=False)
        data.purchases.to_excel(writer, sheet_name="input_vat", index=False)
        data.gl.to_excel(writer, sheet_name="gl_movement", index=False)
        data.payments_refunds.to_excel(writer, sheet_name="payments_refunds", index=False)
        result.exceptions.to_excel(writer, sheet_name="exceptions", index=False)
        return_recon_df.to_excel(writer, sheet_name="reconciling_items", index=False)

    return path

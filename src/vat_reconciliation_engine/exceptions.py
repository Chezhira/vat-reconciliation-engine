from __future__ import annotations

import pandas as pd


def exception_row(
    exception_type: str,
    source: str,
    reference: str,
    amount: float,
    detail: str,
) -> dict:
    return {
        "exception_type": exception_type,
        "source": source,
        "reference": reference,
        "amount": round(float(amount), 2),
        "detail": detail,
    }


def as_exception_frame(rows: list[dict]) -> pd.DataFrame:
    columns = ["exception_type", "source", "reference", "amount", "detail"]
    return pd.DataFrame(rows, columns=columns)

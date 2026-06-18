from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from vat_reconciliation_engine.schema import validate_dataframe


@dataclass(frozen=True)
class VatSourceData:
    sales: pd.DataFrame
    purchases: pd.DataFrame
    vat_return: pd.DataFrame
    gl: pd.DataFrame
    payments_refunds: pd.DataFrame


DATASET_ATTRS = {
    "sales": "sales",
    "purchases": "purchases",
    "vat_return": "vat_return",
    "gl": "gl",
    "payments_refunds": "payments_refunds",
}


def load_dataset(data_dir: str | Path, dataset: str, config: dict) -> pd.DataFrame:
    dataset_config = config["datasets"][dataset]
    path = Path(data_dir) / dataset_config["file"]
    df = pd.read_csv(path)
    validate_dataframe(df, dataset, config)
    return df


def load_sample_data(data_dir: str | Path, config: dict) -> VatSourceData:
    frames = {
        attr: load_dataset(data_dir, dataset, config) for dataset, attr in DATASET_ATTRS.items()
    }
    return VatSourceData(**frames)

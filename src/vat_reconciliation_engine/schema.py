from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class SchemaIssue:
    dataset: str
    missing_fields: tuple[str, ...]

    @property
    def message(self) -> str:
        fields = ", ".join(self.missing_fields)
        return f"{self.dataset} is missing mandatory field(s): {fields}"


class SchemaValidationError(ValueError):
    """Raised when a loaded source file does not match the configured schema."""


def mandatory_fields_for(config: dict, dataset: str) -> list[str]:
    try:
        fields = config["datasets"][dataset]["mandatory_fields"]
    except KeyError as exc:
        raise KeyError(f"Dataset is not configured: {dataset}") from exc
    return list(fields)


def validate_dataframe(df: pd.DataFrame, dataset: str, config: dict) -> None:
    required = mandatory_fields_for(config, dataset)
    missing = tuple(field for field in required if field not in df.columns)
    if missing:
        raise SchemaValidationError(SchemaIssue(dataset, missing).message)

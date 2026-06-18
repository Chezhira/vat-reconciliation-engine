from __future__ import annotations

import pandas as pd
import pytest
from vat_reconciliation_engine.config_loader import load_config
from vat_reconciliation_engine.ingestion import load_dataset, load_sample_data
from vat_reconciliation_engine.schema import SchemaValidationError, validate_dataframe


def test_loads_all_configured_sample_datasets(project_root):
    config = load_config(project_root / "config" / "vat_generic.yml")

    data = load_sample_data(project_root / "data" / "sample", config)

    assert not data.sales.empty
    assert not data.purchases.empty
    assert not data.vat_return.empty
    assert not data.gl.empty
    assert not data.payments_refunds.empty


def test_each_sample_file_matches_configured_schema(project_root):
    config = load_config(project_root / "config" / "vat_generic.yml")

    for dataset in config["datasets"]:
        frame = load_dataset(project_root / "data" / "sample", dataset, config)
        expected = set(config["datasets"][dataset]["mandatory_fields"])
        assert expected.issubset(frame.columns)


def test_schema_validation_reports_missing_required_fields(project_root):
    config = load_config(project_root / "config" / "vat_generic.yml")
    frame = pd.DataFrame(
        [
            {
                "invoice_id": "SINV-TEST",
                "invoice_date": "2026-03-01",
                "customer_name": "Synthetic Customer",
                "tax_code": "standard",
                "net_amount": 100.0,
                "vat_amount": 18.0,
            }
        ]
    )

    with pytest.raises(SchemaValidationError, match="tax_invoice_ref"):
        validate_dataframe(frame, "sales", config)

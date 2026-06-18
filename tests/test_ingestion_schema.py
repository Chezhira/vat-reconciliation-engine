from __future__ import annotations

from io import StringIO

import pandas as pd
import pytest

from vat_reconciliation_engine.config_loader import load_config
from vat_reconciliation_engine.ingestion import (
    DATASET_LABELS,
    load_dataset,
    load_sample_data,
    load_uploaded_data,
    missing_upload_datasets,
    required_upload_datasets,
)
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


def test_upload_helpers_define_required_dataset_order_and_labels():
    assert required_upload_datasets() == [
        "sales",
        "purchases",
        "vat_return",
        "gl",
        "payments_refunds",
    ]
    assert DATASET_LABELS["sales"] == "Sales VAT register"
    assert DATASET_LABELS["payments_refunds"] == "VAT payments/refunds"


def test_missing_upload_datasets_reports_required_gaps():
    uploaded_files = {
        "sales": StringIO("invoice_id\nSINV-TEST\n"),
        "purchases": None,
    }

    assert missing_upload_datasets(uploaded_files) == [
        "purchases",
        "vat_return",
        "gl",
        "payments_refunds",
    ]


def test_loads_uploaded_csv_files_with_same_schema_validation(project_root):
    config = load_config(project_root / "config" / "vat_generic.yml")
    uploaded_files = {}
    for dataset in required_upload_datasets():
        sample_frame = load_dataset(project_root / "data" / "sample", dataset, config)
        uploaded_files[dataset] = StringIO(sample_frame.to_csv(index=False))

    data = load_uploaded_data(uploaded_files, config)

    assert len(data.sales) == 5
    assert len(data.purchases) == 5
    assert len(data.vat_return) == 3
    assert len(data.gl) == 8
    assert len(data.payments_refunds) == 1


def test_uploaded_csv_schema_errors_are_raised(project_root):
    config = load_config(project_root / "config" / "vat_generic.yml")
    uploaded_files = {}
    for dataset in required_upload_datasets():
        sample_frame = load_dataset(project_root / "data" / "sample", dataset, config)
        if dataset == "sales":
            sample_frame = sample_frame.drop(columns=["tax_invoice_ref"])
        uploaded_files[dataset] = StringIO(sample_frame.to_csv(index=False))

    with pytest.raises(SchemaValidationError, match="sales is missing"):
        load_uploaded_data(uploaded_files, config)

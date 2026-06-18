from __future__ import annotations

from vat_reconciliation_engine.config_loader import load_config
from vat_reconciliation_engine.ingestion import load_sample_data
from vat_reconciliation_engine.reconciliation import build_reconciliation


def test_builds_three_core_reconciliation_rules(project_root):
    config = load_config(project_root / "config" / "vat_generic.yml")
    data = load_sample_data(project_root / "data" / "sample", config)

    result = build_reconciliation(data, config)

    assert [item["rule"] for item in result.return_reconciliation] == [
        "VAT return output mismatch",
        "VAT return input mismatch",
        "GL control account variance",
    ]
    assert result.summary.output_vat_variance == 0.0
    assert result.summary.input_vat_variance == 0.0
    assert result.summary.gl_control_variance == 12.0
    assert "GL control account variance" in set(result.exceptions["exception_type"])

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main() -> int:
    from vat_reconciliation_engine.config_loader import load_config
    from vat_reconciliation_engine.exporter import export_exception_workbook
    from vat_reconciliation_engine.ingestion import load_sample_data
    from vat_reconciliation_engine.reconciliation import build_reconciliation

    config = load_config(ROOT / "config" / "vat_generic.yml")
    data = load_sample_data(ROOT / "data" / "sample", config)
    result = build_reconciliation(data, config)
    output = export_exception_workbook(
        data,
        result,
        ROOT / "outputs" / "sample_vat_recon" / "sample_vat_exception_workbook.xlsx",
    )
    print(f"sample workbook: {output.name}")
    print(f"exceptions: {len(result.exceptions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

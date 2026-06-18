from __future__ import annotations


def tax_rate_for_code(tax_code: str, config: dict) -> float:
    rates = config.get("vat_rates", {})
    if tax_code not in rates:
        raise ValueError(f"Unsupported tax code: {tax_code}")
    return float(rates[tax_code])

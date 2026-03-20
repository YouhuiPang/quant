from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class IBKRContractSpec:
    symbol: str
    sec_type: str = "STK"
    exchange: str = "SMART"
    currency: str = "USD"
    primary_exchange: str = ""


def build_contract_definition(symbol_config: dict[str, Any]) -> dict[str, Any]:
    """Build a normalized IBKR contract definition from internal symbol config."""
    spec = IBKRContractSpec(
        symbol=symbol_config["symbol"],
        sec_type=symbol_config.get("sec_type", "STK"),
        exchange=symbol_config.get("exchange", "SMART"),
        currency=symbol_config.get("currency", "USD"),
        primary_exchange=symbol_config.get("primary_exchange", ""),
    )
    return {
        "symbol": spec.symbol,
        "secType": spec.sec_type,
        "exchange": spec.exchange,
        "currency": spec.currency,
        "primaryExchange": spec.primary_exchange,
    }

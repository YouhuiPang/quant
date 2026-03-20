# Architecture

## Why Adapters Are Isolated

IBKR-specific logic is intentionally isolated behind:

- `src/data/adapters/`
- `src/brokers/`
- `src/brokers/ibkr_models.py`

This keeps the rest of the platform independent from raw TWS / IB Gateway callback structures. Research, backtesting, signals, and dashboard views only consume normalized internal schemas.

## Normalized Schema Boundary

The platform normalizes IBKR data into internal objects such as:

- market bars
- latest snapshots
- account snapshots
- position snapshots
- internal orders
- internal fills

This decouples the research and monitoring layers from broker-specific payloads and makes future broker integrations possible without rewriting the platform core.

## End-to-End Data Flow

Historical research flow:

1. IBKR historical adapter
2. normalized cached market data
3. preprocessing and validation
4. features
5. signals
6. target positions
7. risk-adjusted targets
8. backtest and analytics

Live-like monitoring flow:

1. IBKR market/account adapters or local paper state
2. normalized snapshots
3. SQLite persistence
4. dashboard monitoring pages

Execution flow:

1. approved targets
2. broker-aware order generation
3. paper broker or future IBKR broker submission
4. fills
5. position/account snapshots

## Paper vs Live Separation

The runtime is designed to be safe by default:

- data can come from IBKR while execution still remains paper
- broker provider can remain paper even if data provider is IBKR
- IBKR live orders require explicit config flags

This lets the platform use IBKR for market and account data without enabling live trading.

## Research vs Broker Responsibilities

Research remains local and reproducible:

- cached normalized data lives under `data/raw/` or `data/processed/`
- research pipeline never depends on active dashboard callbacks
- features are never built directly from live broker callbacks

Broker/data adapters only provide standardized data into the local cache and state store.

## Persistence Model

SQLite stores live-like monitoring state:

- orders
- fills
- positions
- account snapshots
- market snapshots
- broker status
- risk events

CSV / JSON outputs store research artifacts:

- signals
- targets
- approved targets
- returns
- benchmark returns
- metrics

## Future Real Execution Path

The future real execution path is already prepared conceptually:

1. replace stubbed IBKR request methods with full callback-driven implementations
2. preserve internal order models
3. preserve risk checks before order submission
4. preserve state persistence and dashboard monitoring

That means future real execution can be added without architectural rework across the rest of the platform.

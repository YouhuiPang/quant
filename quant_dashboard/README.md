# Quant Platform v3 with IBKR Integration Architecture

Quant Platform v3 is a local-first quantitative research and monitoring platform that now includes a professional Interactive Brokers integration layer. The system keeps research reproducible by normalizing IBKR data into local cached datasets before those datasets flow into preprocessing, features, signals, portfolio construction, risk checks, backtests, and dashboard monitoring.

## IBKR Integration Design

IBKR is integrated through isolated adapter and broker layers:

- `src/data/adapters/`: historical and market-data adapters
- `src/brokers/`: broker abstraction, paper broker, IBKR broker
- `src/brokers/ibkr_models.py`: centralized contract mapping

The rest of the platform depends on normalized internal schemas instead of raw IBKR callback payloads.

## TWS vs IB Gateway Assumptions

The configuration supports both TWS and IB Gateway style connectivity. For this version:

- the architecture is IBKR-ready
- connection settings are configurable
- historical sync and snapshot flows are supported
- live order placement is disabled by default

## Safe Defaults

The default runtime mode is still safe and paper-first:

- `runtime.mode: paper`
- `runtime.data_provider: csv`
- `runtime.broker_provider: paper`
- `ibkr.readonly_mode: true`
- `ibkr.enable_live_orders: false`
- `ibkr.confirm_live_orders: false`

Even if you switch to `broker_provider: ibkr`, live order submission stays blocked unless both live-order flags are explicitly enabled.

## Installation

```bash
pip install -r requirements.txt
```

## IBKR Configuration

Configure in `config/config.yaml`:

- host
- port
- client_id
- readonly_mode
- account_id
- use_ib_gateway
- market_data_type

Also configure:

- `runtime.data_provider`
- `runtime.broker_provider`
- `data_sync.symbols`
- `paths.market_cache_path`

## Connection Test

Run:

```bash
python scripts/test_ibkr_connection.py
```

This validates that the configured adapter can attempt a connection using the configured host, port, and client id.

## Historical Data Sync

Run:

```bash
python scripts/sync_ibkr_data.py
```

This will:

1. connect to IBKR
2. request historical bars for configured symbols
3. normalize bars into internal OHLCV schema
4. cache them to `data/raw/ibkr_historical_cache.csv`
5. store latest snapshots in SQLite and dashboard outputs

The research pipeline can then use that cached data by setting:

```yaml
runtime:
  data_provider: ibkr
```

The pipeline still consumes local normalized data, not raw broker payloads.

## Running the Research Pipeline

```bash
python scripts/run_pipeline.py
```

## Running the Paper Session

```bash
python scripts/run_paper_session.py
```

This remains paper-safe by default and writes local order, fill, position, and account outputs.

## Launching the Dashboard

```bash
python app.py
```

The dashboard now exposes:

- provider mode
- broker mode
- latest cached market snapshot timestamp
- account snapshot
- positions snapshot
- risk status

## Running Tests

```bash
pytest
```

## Acceptance Validation

```bash
python scripts/validate_outputs.py
```

The acceptance script checks:

- output files
- sqlite state store
- normalized research datasets
- provider and broker safety consistency
- market snapshot availability when IBKR mode is enabled
- account snapshot availability

## Future Extensions

- full ibapi callback wiring for historical and real-time streams
- broker order acknowledgement normalization
- streaming cache refresh worker
- multi-account support
- richer contract resolution for options and futures

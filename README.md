# quant

Quantitative trading research and tooling: data, signals, backtests, and execution glue code.

## Layout (suggested)

- `data/` — raw and processed market data (keep large files out of git; use `.gitignore`)
- `notebooks/` — exploratory analysis
- `src/` — reusable library code (factors, risk, execution helpers)

## Getting started

1. Clone the repository.
2. Add a Python (or other) environment and pin dependencies when you introduce them.
3. Never commit API keys, broker credentials, or proprietary datasets.

## License

MIT — see [LICENSE](LICENSE).

# quant

Quantitative trading research and tooling: data, signals, backtests, and execution glue code.

## Layout (suggested)

- `data/` — raw and processed market data (keep large files out of git; use `.gitignore`)
- `notebooks/` — exploratory analysis
- `src/` — reusable library code (factors, risk, execution helpers)

## Getting started

1. Clone the repository.
2. Create or activate the local Python environment:
   - PowerShell: `.venv\Scripts\Activate.ps1`
   - CMD: `.venv\Scripts\activate.bat`
3. Upgrade `pip` and install dependencies after you add them:
   - `python -m pip install --upgrade pip`
   - `pip install -r requirements.txt`
4. Never commit API keys, broker credentials, or proprietary datasets.

## License

MIT — see [LICENSE](LICENSE).

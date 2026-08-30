# Codex Stock Investigation Skill

Use Codex to investigate why a US stock moved on a specific date, then generate a sourced interactive HTML dashboard.

The Skill checks four evidence layers:

- Market and benchmark performance
- Sector and direct peers
- Company news, earnings, guidance, calls, and SEC filings
- Positioning and liquidity evidence

It keeps regular-session and after-hours events separate, labels conclusions as confirmed, inference, or unknown, and preserves original source links.

## Install with Codex

Ask Codex:

```text
Use $skill-installer to install the stock-investigation skill from
https://github.com/DistillAI888/stock-investigate-skill/tree/main/stock-investigation
```

The Skill will be available on the next turn after installation.

## Use

```text
$stock-investigation SNDK 2026-08-05
```

The ticker is required. The date, benchmark, sector ETF, peers, output language, and a specific investigation question are optional.

Example with explicit comparison symbols:

```text
Use $stock-investigation to investigate COHR on 2026-07-30.
Compare it with QQQ, SOXX, LITE, and IIVI, then generate the Traditional Chinese HTML report.
```

## Output

```text
reports/investigations/TICKER-YYYY-MM-DD/
├── evidence.json
├── analysis.json
├── report.md
└── index.html
```

`index.html` is a static dashboard that uses TradingView Lightweight Charts. It does not require React, Node.js, a backend, or a build step. An internet connection is required to load the chart library and open linked sources.

## Local requirements

- Python 3.10+
- `pandas`
- `yfinance`

Codex can create a project-local virtual environment and install the missing Python packages when needed.

## Important

This project is a research workflow, not a trading signal or investment-advice system. News near a price move is not proof of causation.

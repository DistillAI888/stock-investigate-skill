---
name: stock-investigation
description: Investigate an unusual US-stock price move with market, peer, company-event, SEC, earnings-call, and positioning evidence, then generate a sourced interactive HTML dashboard. Use when Codex needs to explain why a stock moved on a specific date or turn a morning-brief anomaly into a deep-dive report. Do not use for valuation-only research or direct buy/sell recommendations.
---

# Stock Investigation

Turn a ticker and investigation date into an evidence-first interactive HTML report. Keep deterministic calculations separate from narrative research.

## Inputs

- Required: US-listed ticker.
- Optional: investigation date (`YYYY-MM-DD`), benchmark, sector ETF, peers, output language, and a specific question.
- If the date is omitted, use the latest completed US session that triggered the user's anomaly screen. If no screen is available, select the largest recent absolute return weighted by RVOL and disclose that choice.
- Choose peers from the company's actual business exposure. Do not reuse SNDK-specific peers for unrelated companies.

## Workflow

1. Read [references/methodology.md](references/methodology.md) before researching causes.
2. Resolve paths relative to this Skill directory. Run `scripts/collect_market_evidence.py` to create deterministic price, volume, RVOL, market, sector, peer, Yahoo news, and SEC-link evidence.
3. Research the event window using primary sources first: company investor relations, SEC EDGAR, earnings releases, guidance, and the earnings-call transcript. Use established reporting for market reaction and positioning context.
4. Align every event with the US session: pre-market, regular session, after-hours, or non-trading day. An event published after the close cannot explain that day's regular-session move.
5. Write `analysis.json` using [references/output-contract.md](references/output-contract.md). Label each finding `confirmed`, `inference`, or `unknown`.
6. Run `scripts/render_dashboard.py` with the evidence and analysis files. The output must be a static `index.html`; do not require React, Node, a backend, or a build step.
7. Open the report and verify the investigation date, chart, timeframe controls, event links, quarterly table, findings, peer comparison, warnings, and source links.

Recommended output layout:

```text
reports/investigations/TICKER-YYYY-MM-DD/
├── evidence.json
├── analysis.json
├── report.md
└── index.html
```

## Commands

Run the scripts from this Skill directory and pass absolute output paths:

```bash
python scripts/collect_market_evidence.py \
  --ticker SNDK \
  --date 2026-08-05 \
  --benchmark QQQ \
  --sector SOXX \
  --peers WDC,MU \
  --output /absolute/path/reports/investigations/SNDK-2026-08-05/evidence.json

python scripts/render_dashboard.py \
  --evidence /absolute/path/reports/investigations/SNDK-2026-08-05/evidence.json \
  --analysis /absolute/path/reports/investigations/SNDK-2026-08-05/analysis.json \
  --output /absolute/path/reports/investigations/SNDK-2026-08-05/index.html
```

Use the project's virtual environment when one exists. If `pandas` or `yfinance` is missing, create a project-local virtual environment and install only those packages after the normal permission prompt.

## Non-negotiable Rules

- Treat RVOL as a screening measurement, not a trading signal.
- Preserve exact timestamps, publishers, and original URLs.
- Never claim causation from proximity alone. A confirmed cause needs compatible timing and direct evidence or an explicit market reaction source.
- Keep regular-session and after-hours reactions separate.
- Do not invent a catalyst. Write `unknown` when the search does not establish one.
- Do not use filings published after the investigation cutoff as if they were contemporaneously available. They may appear only as later confirmation.
- Do not provide buy/sell instructions or personalized investment advice.

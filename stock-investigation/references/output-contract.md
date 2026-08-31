# Output contract

Create `analysis.json` as valid UTF-8 JSON. Use `null` or an empty array for unavailable fields; never invent values to satisfy the schema. Keep numeric display strings explicit about units and accounting basis.

## Required shape

```json
{
  "company_name": "Sandisk Corporation",
  "headline": "Why did the stock move in and after the session?",
  "deck": "One-sentence scope and time-boundary description.",
  "language": "zh-CN",
  "macro_context": [
    {
      "status": "confirmed",
      "occurred_at": "2026-08-05T10:00:00-04:00",
      "title": "Relevant macro or policy event",
      "detail": "What changed and whether timing overlaps the move.",
      "source_name": "Primary publisher",
      "source_url": "https://..."
    }
  ],
  "quarterly": [
    {
      "quarter": "FY26 Q4",
      "reported_at": "2026-08-05T16:05:00-04:00",
      "revenue_actual": "$8.965B",
      "revenue_estimate": "$8.480B",
      "revenue_surprise": "+5.7%",
      "eps_actual": "$39.25",
      "eps_estimate": "$34.96",
      "eps_surprise": "+12.3%",
      "gross_margin": "84.6%",
      "basis": "non-GAAP",
      "source_url": "https://..."
    }
  ],
  "guidance": [
    {
      "period": "FY27 Q1",
      "metric": "Revenue",
      "company_range": "$10.3B–$10.8B",
      "midpoint": "$10.55B",
      "consensus": "$10.82B",
      "midpoint_vs_consensus": "-2.5%",
      "basis": "company guidance versus FactSet consensus",
      "source_url": "https://..."
    }
  ],
  "business_segments": [
    {
      "name": "Data center",
      "actual": "$2.98B",
      "estimate": "$2.74B",
      "change": "+8.8% versus consensus",
      "why_it_matters": "Material driver discussed by management.",
      "source_url": "https://..."
    }
  ],
  "findings": [
    {
      "status": "confirmed",
      "title": "Short causal conclusion",
      "detail": "What the evidence establishes and the applicable session.",
      "source_urls": ["https://..."]
    }
  ],
  "events": [
    {
      "market_date": "2026-08-05",
      "occurred_at": "2026-08-05T16:05:00-04:00",
      "session": "after-hours",
      "type": "earnings",
      "title": "Company released earnings",
      "summary": "What changed and why it matters.",
      "evidence_level": "A",
      "source_name": "Company IR",
      "source_url": "https://..."
    }
  ],
  "positioning": [
    {
      "status": "inference",
      "as_of": "2026-07-31",
      "title": "Possible liquidity pressure",
      "detail": "Evidence, timing, and limitation.",
      "source_url": "https://..."
    }
  ],
  "sentiment": [
    {
      "status": "inference",
      "as_of": "2026-08-05",
      "metric": "Put/call open-interest ratio",
      "value": "1.21",
      "interpretation": "What it suggests and why it does not prove causation.",
      "source_name": "Exchange or data publisher",
      "source_url": "https://..."
    }
  ],
  "technical_summary": {
    "regime": "Above long-term trend with expanding volatility",
    "summary": "Concise interpretation of deterministic price-volume evidence.",
    "observations": [
      {
        "label": "Price and volume",
        "value": "-5.4% / 1.00x RVOL",
        "interpretation": "Large price move without abnormal volume."
      }
    ]
  },
  "warnings": ["Any unavailable, stale, delayed, or lower-quality evidence."],
  "summary_markdown": "A concise Markdown summary for report.md."
}
```

For backward compatibility, the renderer accepts `revenue` and `eps`, but new reports must use `revenue_actual` and `eps_actual`.

## Allowed values

- `findings[].status`, `macro_context[].status`, `positioning[].status`, and `sentiment[].status`: `confirmed`, `inference`, or `unknown`.
- `events[].session`: `pre-market`, `regular`, `after-hours`, or `non-trading-day`.
- `events[].type`: `macro`, `earnings`, `guidance`, `news`, `sec`, `analyst`, `management`, `m-and-a`, `financing`, `legal`, `positioning`, `sentiment`, or `other`.
- `events[].evidence_level`: `A`, `B`, or `C`.

## Dashboard order

The rendered HTML must keep this order:

1. Investigation title and session snapshot.
2. Interactive candlestick and volume chart with 1M, 3M, 6M, and 1Y controls, event markers, and SMA20/SMA50 overlays.
3. Company fundamentals: actual versus consensus revenue and EPS, gross margin, guidance versus consensus, and relevant business segments.
4. Investigation findings separated into confirmed, inference, and unknown.
5. Macro and market context, followed by market, sector, and peer comparison.
6. Company-event timeline with pre-market, regular, and after-hours labels.
7. Positioning and sentiment evidence with visible `as_of` dates.
8. Technical and price-volume section using deterministic evidence plus a concise interpretation.
9. Data warnings and all source links.

The page must state that it does not constitute investment advice.

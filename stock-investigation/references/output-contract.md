# Output contract

Create `analysis.json` as valid UTF-8 JSON. Use `null` or an empty array for unavailable fields; never invent values to satisfy the schema.

## Required shape

```json
{
  "company_name": "Sandisk Corporation",
  "headline": "8 月 5 日盤中下跌，為什麼盤後又繼續跌？",
  "deck": "One-sentence scope and time-boundary description.",
  "language": "zh-TW",
  "quarterly": [
    {
      "quarter": "FY26 Q4",
      "reported_at": "2026-08-05T16:05:00-04:00",
      "revenue": "$8.965B",
      "eps": "$39.25",
      "gross_margin": "84.6%",
      "source_url": "https://..."
    }
  ],
  "findings": [
    {
      "status": "confirmed",
      "title": "Short conclusion",
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
      "title": "Possible liquidity pressure",
      "detail": "Evidence and limitation.",
      "source_url": "https://..."
    }
  ],
  "warnings": ["Any unavailable, stale, delayed, or lower-quality evidence."],
  "summary_markdown": "A concise Markdown summary for report.md."
}
```

## Allowed values

- `findings[].status`: `confirmed`, `inference`, or `unknown`.
- `events[].session`: `pre-market`, `regular`, `after-hours`, or `non-trading-day`.
- `events[].type`: `earnings`, `guidance`, `news`, `sec`, `analyst`, `management`, `m-and-a`, `financing`, `legal`, `positioning`, or `other`.
- `events[].evidence_level`: `A`, `B`, or `C`.

## Dashboard order

The rendered HTML must keep this order:

1. Investigation title and session snapshot.
2. Interactive candlestick and volume chart with 1M, 3M, 6M, and 1Y controls.
3. Earnings and major-event markers. Hovering the corresponding bar shows the title, summary, and original link.
4. Recent-quarter revenue, EPS, and gross-margin table with primary-source links.
5. Investigation findings separated into confirmed, inference, and unknown.
6. Market, sector, and peer comparison for the investigation session.
7. Company-event timeline with pre-market, regular, and after-hours labels.
8. Positioning/liquidity evidence.
9. Data warnings and all source links.

The page must state that it does not constitute investment advice.

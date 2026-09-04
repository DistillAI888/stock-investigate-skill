# Output contract

Create `analysis.json` as valid UTF-8 JSON. Use `null` or an empty array for unavailable fields; never invent values to satisfy the schema. Keep numeric display strings explicit about units and accounting basis.

Use Simplified Chinese (`zh-CN`) for all reader-facing narrative fields by default. Use another language only when the user explicitly requests it.

## Required shape

```json
{
  "company_name": "Sandisk Corporation",
  "headline": "这只股票为何在盘中及盘后异动？",
  "deck": "用一句话说明调查范围和时间边界。",
  "language": "zh-CN",
  "macro_context": [
    {
      "status": "confirmed",
      "occurred_at": "2026-08-05T10:00:00-04:00",
      "title": "相关宏观或政策事件",
      "detail": "说明发生了什么变化，以及时间是否与异动重合。",
      "source_name": "一手发布机构",
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
      "metric": "营收",
      "company_range": "$10.3B–$10.8B",
      "midpoint": "$10.55B",
      "consensus": "$10.82B",
      "midpoint_vs_consensus": "-2.5%",
      "basis": "公司指引与 FactSet 市场共识对比",
      "source_url": "https://..."
    }
  ],
  "business_segments": [
    {
      "name": "数据中心",
      "actual": "$2.98B",
      "estimate": "$2.74B",
      "change": "较市场共识高 8.8%",
      "why_it_matters": "管理层讨论的关键驱动因素。",
      "source_url": "https://..."
    }
  ],
  "findings": [
    {
      "status": "confirmed",
      "title": "简短的因果结论",
      "detail": "说明证据可以确认什么，以及适用的交易时段。",
      "source_urls": ["https://..."]
    }
  ],
  "events": [
    {
      "market_date": "2026-08-05",
      "occurred_at": "2026-08-05T16:05:00-04:00",
      "session": "after-hours",
      "type": "earnings",
      "title": "公司发布财报",
      "summary": "说明发生了什么变化及其重要性。",
      "evidence_level": "A",
      "source_name": "公司投资者关系网站",
      "source_url": "https://..."
    }
  ],
  "positioning": [
    {
      "status": "inference",
      "as_of": "2026-07-31",
      "title": "可能存在流动性压力",
      "detail": "说明证据、时间和局限性。",
      "source_url": "https://..."
    }
  ],
  "sentiment": [
    {
      "status": "inference",
      "as_of": "2026-08-05",
      "metric": "看跌/看涨期权未平仓量比率",
      "value": "1.21",
      "interpretation": "说明该指标可能意味着什么，以及为何不能据此证明因果关系。",
      "source_name": "交易所或数据发布方",
      "source_url": "https://..."
    }
  ],
  "technical_summary": {
    "regime": "位于长期趋势上方，波动率正在扩大",
    "summary": "对确定性量价证据的简明解读。",
    "observations": [
      {
        "label": "价格与成交量",
        "value": "-5.4% / 1.00x RVOL",
        "interpretation": "价格波动较大，但成交量没有明显异常。"
      }
    ]
  },
  "warnings": ["列出任何缺失、过期、延迟或质量较低的证据。"],
  "summary_markdown": "供 report.md 使用的简明 Markdown 摘要。"
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

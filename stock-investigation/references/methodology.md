# Investigation methodology

## Four-layer checklist

Investigate all relevant layers and state when one was already screened by an upstream morning brief.

1. **Market:** Compare the stock with broad benchmarks such as SPY or QQQ. A stock can be unusually weak even when the market also falls.
2. **Industry:** Compare a sector ETF and directly exposed peers on the same completed session. Mixed peer evidence must remain mixed.
3. **Company events:** Check news, investor-relations releases, earnings, guidance, the call transcript, analyst actions, management changes, M&A, financing, orders, legal matters, and SEC filings.
4. **Positioning and liquidity:** Check Form 4, Schedule 13D/13G, Form 13F, index changes, options-related events, short covering, forced selling, and credible reporting about concentrated holders.

## Time alignment

Use America/New_York for US-market event timing.

- Pre-market: before 09:30 ET.
- Regular session: 09:30–16:00 ET.
- After-hours: after 16:00 ET.
- An after-hours earnings release may explain after-hours and the next session, but not the already-completed regular session.
- For a non-trading-day event, state which next trading session could first react.

Keep `occurred_at` as the exact event time when available. Use `market_date` only to place the marker on an actual trading bar.

## Evidence levels

- **confirmed:** The timing is compatible and a primary source, company statement, filing, transcript, or explicit contemporaneous market-reaction report directly supports the finding.
- **inference:** The timing and evidence are compatible, but causation is not directly established. Explain the missing link.
- **unknown:** No reliable event or evidence was found that explains the move. List what was checked.

Source quality:

- **A:** SEC filing, company investor-relations release, official presentation, or official transcript.
- **B:** Established financial-news reporting, exchange data, or a named analyst note reported by a credible publisher.
- **C:** Commentary, aggregation, social posts, rumor, or an unclear source.

Do not upgrade a C-level claim because many sites repeat it.

## Filing boundaries

- 8-K: material current reports and attached releases.
- 10-Q / 10-K: periodic financial and risk disclosures.
- Form 4: insider transactions, not automatically insider conviction.
- Schedule 13D / 13G: beneficial ownership disclosures with filing delay.
- Form 13F: quarterly institutional holdings, due up to 45 days after quarter end; it cannot prove a specific intraday trade.

Record both the event date and filing/publication date. Later filings may confirm background but must not be presented as information available at the investigation cutoff.

## Price calculations

- `1d_return`: latest close divided by previous close minus one.
- `5d_return`: latest close divided by the close five sessions earlier minus one.
- `gap`: current open divided by previous close minus one.
- `rvol20`: current volume divided by the mean of the preceding 20 completed sessions.
- `relative_to_benchmark`: stock 1-day return minus benchmark 1-day return.

Use unadjusted OHLC for the displayed session and disclose material splits when they distort comparisons.

# Investigation methodology

## Five-layer checklist

Investigate every relevant layer. If an upstream morning brief already screened a layer, summarize that evidence instead of silently skipping it.

### 1. Macro and market

- Compare the stock with broad benchmarks such as SPY or QQQ.
- Check market-observable macro proxies around the session: volatility, Treasury duration or yields, and the US dollar. The collection script defaults to VIX, TLT, and UUP.
- Search the event window for scheduled and unscheduled macro catalysts: FOMC decisions or speeches, CPI/PCE, payrolls, GDP, Treasury auctions, tariffs, sanctions, and material fiscal or regulatory announcements.
- Prefer the Federal Reserve, BLS, BEA, US Treasury, and other first-party releases. Preserve both release time and reference period.
- Do not treat a monthly observation date as the date investors learned the number. For delayed series, use the publication time known to the market.

### 2. Industry

- Compare a sector ETF and directly exposed peers on the same completed session.
- Choose peers by revenue exposure and product competition, not merely by a website's sector label.
- Check industry-specific inputs such as commodity prices, memory or freight pricing, reimbursement, regulation, or supply-chain news when relevant.
- Mixed peer evidence must remain mixed. A sector decline does not automatically explain a much larger company-specific move.

### 3. Company fundamentals and events

- Check investor-relations releases, SEC filings, news, earnings, guidance, the call transcript, analyst actions, management changes, M&A, financing, orders, legal matters, product events, and customer or supplier disclosures.
- For earnings, record actual revenue and EPS beside contemporaneous consensus. Calculate the surprise only when both figures use the same accounting basis and unit.
- Compare company guidance ranges and midpoints with contemporaneous consensus. Do not compare GAAP guidance with non-GAAP consensus.
- Capture gross margin and the business segments or operating metrics that management and analysts emphasized. Do not fill every segment when it is irrelevant to the move.
- Separate the earnings release, prepared remarks, and analyst Q&A. The Q&A may contain the first direct explanation of a weak guide or changed assumption.
- Record analyst target-price or rating changes with publisher, analyst or firm, timestamp, and prior value when available. Treat reported notes as B-level evidence unless the original note is available.

### 4. Positioning and sentiment

- Check Form 4, Schedule 13D/13G, Form 13F, index changes, options-related events, short covering, forced selling, and credible reporting about concentrated holders.
- When available, record short interest, days to cover, borrow cost, institutional or insider ownership, put/call ratios, unusual options activity, and material changes from a prior comparable snapshot.
- Keep measurement dates visible. Form 13F is delayed, exchange short-interest data is periodic, and the current options chain is not historical evidence.
- Treat social-media tone, rumor, crowd sentiment, and unsourced flow claims as C-level context. Repetition does not upgrade source quality.
- Extreme sentiment can describe a fragile setup or crowded trade, but it does not prove whether a move was caused by long liquidation, short covering, or new information.

### 5. Technical and price-volume structure

- Use deterministic values from `evidence.technical`: SMA20/50/200, RSI14, MACD, ATR14, Bollinger levels, 20-day and 52-week ranges, volume trend, RVOL, and OBV direction.
- Describe where the price sits relative to trend and recent range, whether volatility expanded, and whether volume confirmed or contradicted the move.
- Identify obvious support, resistance, gaps, and prior breakout or breakdown levels only from the displayed price history. Avoid false precision.
- Technical evidence answers how the move behaved, not why it happened. Do not convert an indicator reading into a confirmed catalyst or a buy/sell instruction.

## Time alignment

Use America/New_York for US-market event timing.

- Pre-market: before 09:30 ET.
- Regular session: 09:30–16:00 ET.
- After-hours: after 16:00 ET.
- An after-hours earnings release may explain after-hours and the next session, but not the already-completed regular session.
- For a non-trading-day event, state which next trading session could first react.

Keep `occurred_at` as the exact event time when available. Use `market_date` only to place the marker on an actual trading bar.

## Evidence levels

- **confirmed:** Timing is compatible and a primary source, company statement, filing, transcript, or explicit contemporaneous market-reaction report directly supports the finding.
- **inference:** Timing and evidence are compatible, but causation is not directly established. Explain the missing link.
- **unknown:** No reliable evidence establishes a cause. List what was checked.

Source quality:

- **A:** Government or regulator release, SEC filing, company investor-relations release, official presentation, or official transcript.
- **B:** Established financial-news reporting, exchange data, or a named analyst note reported by a credible publisher.
- **C:** Commentary, aggregation, social posts, rumor, or an unclear source.

Do not upgrade a C-level claim because many sites repeat it.

## Filing boundaries

- 8-K: material current reports and attached releases.
- 10-Q / 10-K: periodic financial and risk disclosures.
- Form 4: insider transactions, not automatically insider conviction.
- Schedule 13D / 13G: beneficial ownership disclosures with filing delay.
- Form 13F: quarterly institutional holdings, due up to 45 days after quarter end; it cannot prove a specific intraday trade.

Record both the event date and filing or publication date. Later filings may confirm background but must not be presented as information available at the investigation cutoff.

## Deterministic calculations

- `1d_return`: latest close divided by previous close minus one.
- `5d_return`: latest close divided by the close five sessions earlier minus one.
- `gap`: current open divided by previous close minus one.
- `rvol20`: current volume divided by the mean of the preceding 20 completed sessions.
- `relative_to_benchmark`: stock 1-day return minus benchmark 1-day return.
- `SMA20/50/200`: simple moving averages of completed-session closes.
- `RSI14`: Wilder-style exponentially smoothed 14-session RSI.
- `MACD`: EMA12 minus EMA26, with a 9-session signal line.
- `ATR14`: 14-session average true range.
- `Bollinger levels`: SMA20 plus or minus two rolling standard deviations.
- `volume_ma5_vs_ma20`: five-session average volume divided by 20-session average volume.

Use unadjusted OHLC for the displayed session and disclose material splits when they distort comparisons.

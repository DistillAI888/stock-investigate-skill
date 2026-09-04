#!/usr/bin/env python3
"""Collect deterministic evidence for one US-stock move investigation."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf


MACRO_LABELS = {
    "^VIX": "VIX 波动率指数",
    "TLT": "长期美国国债 ETF",
    "UUP": "美元指数 ETF",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticker", required=True, help="US-listed ticker symbol")
    parser.add_argument("--date", help="Investigation date in YYYY-MM-DD; defaults to latest session")
    parser.add_argument("--benchmark", default="QQQ")
    parser.add_argument("--sector", default="SOXX")
    parser.add_argument("--peers", default="", help="Comma-separated peer symbols")
    parser.add_argument(
        "--macro-proxies",
        default="^VIX,TLT,UUP",
        help="Comma-separated market-observable macro proxies",
    )
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def number(value: Any, digits: int = 2) -> float | None:
    if value is None or pd.isna(value):
        return None
    return round(float(value), digits)


def integer(value: Any) -> int | None:
    if value is None or pd.isna(value):
        return None
    return int(value)


def unique_symbols(items: list[str]) -> list[str]:
    result: list[str] = []
    for item in items:
        symbol = item.strip().upper()
        if symbol and symbol not in result:
            result.append(symbol)
    return result


def symbol_frame(downloaded: pd.DataFrame, symbol: str, symbol_count: int) -> pd.DataFrame:
    if symbol_count == 1 and not isinstance(downloaded.columns, pd.MultiIndex):
        frame = downloaded.copy()
    else:
        try:
            frame = downloaded[symbol].copy()
        except KeyError as exc:
            raise RuntimeError(f"No market data returned for {symbol}") from exc
    frame = frame.dropna(subset=["Close"])
    if frame.empty:
        raise RuntimeError(f"No market data returned for {symbol}")
    if getattr(frame.index, "tz", None) is not None:
        frame.index = frame.index.tz_localize(None)
    return frame


def session_metrics(frame: pd.DataFrame, target: pd.Timestamp) -> dict[str, Any]:
    eligible = frame.loc[frame.index <= target]
    if eligible.empty:
        raise RuntimeError(f"No completed session on or before {target.date().isoformat()}")
    idx = eligible.index[-1]
    position = frame.index.get_loc(idx)
    if not isinstance(position, int) or position < 1:
        raise RuntimeError("Insufficient history for return calculation")

    row = frame.iloc[position]
    previous = frame.iloc[position - 1]
    prior_20 = frame.iloc[max(0, position - 20):position]["Volume"].astype(float)
    five_back = frame.iloc[max(0, position - 5)]
    mean_volume = float(prior_20.mean()) if not prior_20.empty else None

    return {
        "date": idx.date().isoformat(),
        "open": number(row["Open"]),
        "high": number(row["High"]),
        "low": number(row["Low"]),
        "close": number(row["Close"]),
        "volume": integer(row["Volume"]),
        "return_1d": number((float(row["Close"]) / float(previous["Close"]) - 1) * 100),
        "return_5d": number((float(row["Close"]) / float(five_back["Close"]) - 1) * 100),
        "gap": number((float(row["Open"]) / float(previous["Close"]) - 1) * 100),
        "average_volume_20": integer(mean_volume),
        "rvol20": number(float(row["Volume"]) / mean_volume) if mean_volume else None,
    }


def indicator_series(frame: pd.DataFrame, focus_date: str) -> pd.DataFrame:
    data = frame.loc[frame.index <= pd.Timestamp(focus_date)].copy()
    close = data["Close"].astype(float)
    high = data["High"].astype(float)
    low = data["Low"].astype(float)
    volume = data["Volume"].astype(float)

    data["SMA20"] = close.rolling(20).mean()
    data["SMA50"] = close.rolling(50).mean()
    data["SMA200"] = close.rolling(200).mean()
    data["EMA12"] = close.ewm(span=12, adjust=False).mean()
    data["EMA26"] = close.ewm(span=26, adjust=False).mean()
    data["MACD"] = data["EMA12"] - data["EMA26"]
    data["MACDSignal"] = data["MACD"].ewm(span=9, adjust=False).mean()

    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    rs = gain / loss.replace(0, float("nan"))
    data["RSI14"] = 100 - (100 / (1 + rs))
    data.loc[(loss == 0) & gain.notna(), "RSI14"] = 100

    previous_close = close.shift(1)
    true_range = pd.concat(
        [(high - low), (high - previous_close).abs(), (low - previous_close).abs()], axis=1
    ).max(axis=1)
    data["ATR14"] = true_range.rolling(14).mean()
    data["BBUpper"] = data["SMA20"] + 2 * close.rolling(20).std()
    data["BBLower"] = data["SMA20"] - 2 * close.rolling(20).std()
    data["RVOL20"] = volume / volume.shift(1).rolling(20).mean()
    data["VolumeMA5"] = volume.rolling(5).mean()
    data["VolumeMA20"] = volume.rolling(20).mean()
    direction = close.diff().apply(lambda value: 1 if value > 0 else -1 if value < 0 else 0)
    data["OBV"] = (direction * volume).cumsum()
    return data


def percent_distance(current: float, reference: Any) -> float | None:
    if reference is None or pd.isna(reference) or float(reference) == 0:
        return None
    return number((current / float(reference) - 1) * 100)


def technical_snapshot(frame: pd.DataFrame, focus_date: str) -> dict[str, Any]:
    data = indicator_series(frame, focus_date)
    row = data.iloc[-1]
    close = float(row["Close"])
    trailing_20 = data.tail(20)
    trailing_252 = data.tail(252)
    obv_change_20 = None
    if len(data) > 20:
        obv_change_20 = number(float(data["OBV"].iloc[-1] - data["OBV"].iloc[-21]), 0)

    return {
        "as_of": data.index[-1].date().isoformat(),
        "sma20": number(row["SMA20"]),
        "sma50": number(row["SMA50"]),
        "sma200": number(row["SMA200"]),
        "distance_from_sma20_pct": percent_distance(close, row["SMA20"]),
        "distance_from_sma50_pct": percent_distance(close, row["SMA50"]),
        "distance_from_sma200_pct": percent_distance(close, row["SMA200"]),
        "rsi14": number(row["RSI14"]),
        "macd": number(row["MACD"], 4),
        "macd_signal": number(row["MACDSignal"], 4),
        "macd_histogram": number(row["MACD"] - row["MACDSignal"], 4),
        "atr14": number(row["ATR14"]),
        "atr14_pct": number(float(row["ATR14"]) / close * 100) if not pd.isna(row["ATR14"]) else None,
        "bollinger_upper": number(row["BBUpper"]),
        "bollinger_lower": number(row["BBLower"]),
        "high_20d": number(trailing_20["High"].max()),
        "low_20d": number(trailing_20["Low"].min()),
        "high_52w": number(trailing_252["High"].max()),
        "low_52w": number(trailing_252["Low"].min()),
        "volume_ma5_vs_ma20": number(row["VolumeMA5"] / row["VolumeMA20"])
        if not pd.isna(row["VolumeMA20"]) and float(row["VolumeMA20"]) != 0
        else None,
        "obv_change_20": obv_change_20,
        "obv_trend_20": "rising" if obv_change_20 and obv_change_20 > 0 else "falling" if obv_change_20 and obv_change_20 < 0 else "flat_or_unavailable",
        "limitations": "技术指标描述价格与成交量结构，不能单独证明异动原因。",
    }


def chart_rows(frame: pd.DataFrame, focus_date: str) -> list[dict[str, Any]]:
    visible = indicator_series(frame, focus_date).tail(260)
    returns = visible["Close"].astype(float).pct_change() * 100
    rows: list[dict[str, Any]] = []
    for idx, row in visible.iterrows():
        rows.append(
            {
                "date": idx.date().isoformat(),
                "open": number(row["Open"]),
                "high": number(row["High"]),
                "low": number(row["Low"]),
                "close": number(row["Close"]),
                "volume": integer(row["Volume"]),
                "return": number(returns.loc[idx]),
                "rvol": number(row["RVOL20"]),
                "sma20": number(row["SMA20"]),
                "sma50": number(row["SMA50"]),
            }
        )
    return rows


def serialize_news(ticker: yf.Ticker, symbol: str) -> tuple[list[dict[str, Any]], list[str]]:
    output: list[dict[str, Any]] = []
    try:
        raw_news = ticker.get_news(count=30, tab="all")
    except Exception as exc:  # yfinance upstream failures vary
        return [], [f"Yahoo news unavailable: {exc}"]

    for item in raw_news:
        content = item.get("content", item)
        related = {
            stock.get("symbol")
            for stock in content.get("finance", {}).get("stockTickers", [])
            if isinstance(stock, dict)
        }
        if related and symbol not in related:
            continue
        output.append(
            {
                "published_at": content.get("pubDate") or content.get("providerPublishTime"),
                "title": content.get("title"),
                "summary": content.get("summary"),
                "source_name": (content.get("provider") or {}).get("displayName")
                if isinstance(content.get("provider"), dict)
                else content.get("publisher"),
                "source_url": (content.get("canonicalUrl") or {}).get("url")
                if isinstance(content.get("canonicalUrl"), dict)
                else content.get("link"),
            }
        )
    warnings = [] if output else ["Yahoo news returned no ticker-specific items; perform an independent source search."]
    return output[:20], warnings


def serialize_filings(ticker: yf.Ticker) -> tuple[list[dict[str, Any]], list[str]]:
    output: list[dict[str, Any]] = []
    try:
        filings = ticker.get_sec_filings() or []
    except Exception as exc:
        return [], [f"Yahoo SEC filing index unavailable: {exc}"]
    for filing in filings[:25]:
        filing_date = filing.get("date")
        output.append(
            {
                "filed_at": filing_date.isoformat() if hasattr(filing_date, "isoformat") else filing_date,
                "form": filing.get("type"),
                "title": filing.get("title"),
                "source_url": filing.get("edgarUrl"),
                "exhibits": filing.get("exhibits", {}),
            }
        )
    return output, []


def iso_date_from_epoch(value: Any) -> str | None:
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc).date().isoformat()
    except (TypeError, ValueError, OSError):
        return None


def positioning_snapshot(ticker: yf.Ticker, focus_date: str) -> tuple[dict[str, Any], list[str]]:
    try:
        info = ticker.get_info() or {}
    except Exception as exc:
        return {}, [f"Current positioning snapshot unavailable: {exc}"]

    current_date = datetime.now(timezone.utc).date()
    historical = abs((current_date - date.fromisoformat(focus_date)).days) > 7
    snapshot = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "is_contemporaneous_with_investigation": not historical,
        "short_interest_date": iso_date_from_epoch(info.get("dateShortInterest")),
        "short_percent_of_float": number(info.get("shortPercentOfFloat") * 100)
        if info.get("shortPercentOfFloat") is not None
        else None,
        "short_ratio_days": number(info.get("shortRatio")),
        "shares_short": integer(info.get("sharesShort")),
        "shares_short_prior_month": integer(info.get("sharesShortPriorMonth")),
        "institution_held_percent": number(info.get("heldPercentInstitutions") * 100)
        if info.get("heldPercentInstitutions") is not None
        else None,
        "insider_held_percent": number(info.get("heldPercentInsiders") * 100)
        if info.get("heldPercentInsiders") is not None
        else None,
        "analyst_target_mean": number(info.get("targetMeanPrice")),
        "analyst_target_low": number(info.get("targetLowPrice")),
        "analyst_target_high": number(info.get("targetHighPrice")),
        "recommendation_key": info.get("recommendationKey"),
        "source_name": "Yahoo Finance company snapshot",
        "source_url": info.get("website"),
    }
    warnings = []
    if historical:
        warnings.append(
            "空头、持股和分析师数据属于当前快照，不能作为调查日期的历史证据。"
        )
    return snapshot, warnings


def options_snapshot(ticker: yf.Ticker, focus_date: str) -> tuple[dict[str, Any], list[str]]:
    try:
        expirations = ticker.options or ()
        if not expirations:
            return {}, ["未取得当前上市期权链数据。"]
        expiration = expirations[0]
        chain = ticker.option_chain(expiration)
        call_oi = int(chain.calls.get("openInterest", pd.Series(dtype=float)).fillna(0).sum())
        put_oi = int(chain.puts.get("openInterest", pd.Series(dtype=float)).fillna(0).sum())
        call_volume = int(chain.calls.get("volume", pd.Series(dtype=float)).fillna(0).sum())
        put_volume = int(chain.puts.get("volume", pd.Series(dtype=float)).fillna(0).sum())
    except Exception as exc:
        return {}, [f"Current options snapshot unavailable: {exc}"]

    historical = abs((datetime.now(timezone.utc).date() - date.fromisoformat(focus_date)).days) > 7
    snapshot = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "expiration": expiration,
        "is_contemporaneous_with_investigation": not historical,
        "call_open_interest": call_oi,
        "put_open_interest": put_oi,
        "put_call_open_interest_ratio": number(put_oi / call_oi) if call_oi else None,
        "call_volume": call_volume,
        "put_volume": put_volume,
        "put_call_volume_ratio": number(put_volume / call_volume) if call_volume else None,
        "source_name": "Yahoo Finance 当前期权链",
    }
    warnings = []
    if historical:
        warnings.append(
            "期权链属于当前快照，不能用于解释历史股价异动。"
        )
    return snapshot, warnings


def choose_focus(frame: pd.DataFrame, requested: str | None) -> tuple[str, str]:
    if requested:
        requested_date = date.fromisoformat(requested)
        eligible = frame.loc[frame.index.date <= requested_date]
        if eligible.empty:
            raise RuntimeError(f"No trading session on or before {requested}")
        actual = eligible.index[-1].date().isoformat()
        note = "requested session" if actual == requested else f"previous completed session for non-trading date {requested}"
        return actual, note

    close = frame["Close"].astype(float)
    volume = frame["Volume"].astype(float)
    returns = close.pct_change() * 100
    rvol = volume / volume.shift(1).rolling(20).mean()
    scores = (returns.abs() * rvol.fillna(1)).tail(30).dropna()
    idx = scores.idxmax() if not scores.empty else frame.index[-1]
    return idx.date().isoformat(), "automatically selected from the largest recent absolute return weighted by RVOL"


def main() -> None:
    args = parse_args()
    ticker_symbol = args.ticker.upper()
    benchmark = args.benchmark.upper()
    sector = args.sector.upper()
    peers = unique_symbols(args.peers.split(","))
    macro_symbols = unique_symbols(args.macro_proxies.split(","))
    comparison_symbols = unique_symbols([ticker_symbol, benchmark, sector, *peers])
    symbols = unique_symbols([*comparison_symbols, *macro_symbols])

    if args.date:
        requested_date = date.fromisoformat(args.date)
        start = requested_date - timedelta(days=400)
        end = requested_date + timedelta(days=3)
        downloaded = yf.download(
            symbols,
            start=start.isoformat(),
            end=end.isoformat(),
            auto_adjust=False,
            progress=False,
            group_by="ticker",
        )
    else:
        downloaded = yf.download(
            symbols,
            period="1y",
            auto_adjust=False,
            progress=False,
            group_by="ticker",
        )

    warnings: list[str] = []
    frames: dict[str, pd.DataFrame] = {}
    for symbol in symbols:
        try:
            frames[symbol] = symbol_frame(downloaded, symbol, len(symbols))
        except RuntimeError as exc:
            warnings.append(str(exc))
    if ticker_symbol not in frames:
        raise RuntimeError(f"No market data returned for required ticker {ticker_symbol}")

    focus_date, selection_note = choose_focus(frames[ticker_symbol], args.date)
    target = pd.Timestamp(focus_date)
    metrics: dict[str, dict[str, Any]] = {}
    for symbol, frame in frames.items():
        try:
            metrics[symbol] = session_metrics(frame, target)
        except RuntimeError as exc:
            warnings.append(f"{symbol}: {exc}")

    benchmark_return = (metrics.get(benchmark) or {}).get("return_1d")
    comparisons: list[dict[str, Any]] = []
    for symbol in comparison_symbols:
        item = metrics.get(symbol)
        if not item:
            continue
        comparisons.append(
            {
                "symbol": symbol,
                "role": "stock" if symbol == ticker_symbol else "benchmark" if symbol == benchmark else "sector" if symbol == sector else "peer",
                "date": item["date"],
                "return_1d": item["return_1d"],
                "relative_to_benchmark": number(item["return_1d"] - benchmark_return)
                if benchmark_return is not None
                else None,
            }
        )

    macro_proxies: list[dict[str, Any]] = []
    for symbol in macro_symbols:
        item = metrics.get(symbol)
        if not item:
            continue
        macro_proxies.append(
            {
                "symbol": symbol,
                "label": MACRO_LABELS.get(symbol, symbol),
                "date": item["date"],
                "close": item["close"],
                "return_1d": item["return_1d"],
                "return_5d": item["return_5d"],
                "source_url": f"https://finance.yahoo.com/quote/{symbol}",
            }
        )

    ticker = yf.Ticker(ticker_symbol)
    news, news_warnings = serialize_news(ticker, ticker_symbol)
    filings, filing_warnings = serialize_filings(ticker)
    positioning, positioning_warnings = positioning_snapshot(ticker, focus_date)
    options, options_warnings = options_snapshot(ticker, focus_date)
    warnings.extend(
        [
            "Yahoo Finance / yfinance 属于非官方研究数据源；重要结论应通过一手来源复核。",
            "股价异动附近出现的新闻只能作为背景，不能单独证明因果关系。",
            *news_warnings,
            *filing_warnings,
            *positioning_warnings,
            *options_warnings,
        ]
    )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ticker": ticker_symbol,
        "requested_date": args.date,
        "investigation_date": focus_date,
        "date_selection_note": selection_note,
        "benchmark": benchmark,
        "sector": sector,
        "peers": peers,
        "macro_symbols": macro_symbols,
        "focus": metrics[ticker_symbol],
        "comparisons": comparisons,
        "macro_proxies": macro_proxies,
        "technical": technical_snapshot(frames[ticker_symbol], focus_date),
        "positioning_snapshot": positioning,
        "options_snapshot": options,
        "chart": chart_rows(frames[ticker_symbol], focus_date),
        "news_candidates": news,
        "filing_candidates": filings,
        "warnings": warnings,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.output.resolve())


if __name__ == "__main__":
    main()

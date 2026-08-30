#!/usr/bin/env python3
"""Collect deterministic market evidence for one stock-move investigation."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticker", required=True, help="US-listed ticker symbol")
    parser.add_argument("--date", help="Investigation date in YYYY-MM-DD; defaults to latest session")
    parser.add_argument("--benchmark", default="QQQ")
    parser.add_argument("--sector", default="SOXX")
    parser.add_argument("--peers", default="", help="Comma-separated peer symbols")
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def number(value: Any, digits: int = 2) -> float | None:
    if value is None or pd.isna(value):
        return None
    return round(float(value), digits)


def unique_symbols(items: list[str]) -> list[str]:
    result: list[str] = []
    for item in items:
        symbol = item.strip().upper()
        if symbol and symbol not in result:
            result.append(symbol)
    return result


def symbol_frame(downloaded: pd.DataFrame, symbol: str, symbol_count: int) -> pd.DataFrame:
    if symbol_count == 1:
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
        "volume": int(row["Volume"]),
        "return_1d": number((float(row["Close"]) / float(previous["Close"]) - 1) * 100),
        "return_5d": number((float(row["Close"]) / float(five_back["Close"]) - 1) * 100),
        "gap": number((float(row["Open"]) / float(previous["Close"]) - 1) * 100),
        "average_volume_20": int(mean_volume) if mean_volume else None,
        "rvol20": number(float(row["Volume"]) / mean_volume) if mean_volume else None,
    }


def chart_rows(frame: pd.DataFrame, focus_date: str) -> list[dict[str, Any]]:
    focus = pd.Timestamp(focus_date)
    visible = frame.loc[frame.index <= focus].tail(260).copy()
    close = visible["Close"].astype(float)
    returns = close.pct_change() * 100
    volume = visible["Volume"].astype(float)
    rvol = volume / volume.shift(1).rolling(20).mean()
    rows: list[dict[str, Any]] = []
    for idx, row in visible.iterrows():
        rows.append(
            {
                "date": idx.date().isoformat(),
                "open": number(row["Open"]),
                "high": number(row["High"]),
                "low": number(row["Low"]),
                "close": number(row["Close"]),
                "volume": int(row["Volume"]),
                "return": number(returns.loc[idx]),
                "rvol": number(rvol.loc[idx]),
            }
        )
    return rows


def serialize_news(ticker: yf.Ticker, symbol: str) -> tuple[list[dict[str, Any]], list[str]]:
    output: list[dict[str, Any]] = []
    warnings: list[str] = []
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
    if not output:
        warnings.append("Yahoo news returned no ticker-specific items; perform an independent source search.")
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
    peers = unique_symbols(args.peers.split(","))
    symbols = unique_symbols([ticker_symbol, args.benchmark, args.sector, *peers])

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

    frames = {symbol: symbol_frame(downloaded, symbol, len(symbols)) for symbol in symbols}
    focus_date, selection_note = choose_focus(frames[ticker_symbol], args.date)
    target = pd.Timestamp(focus_date)
    metrics = {symbol: session_metrics(frame, target) for symbol, frame in frames.items()}
    benchmark_return = metrics[args.benchmark.upper()]["return_1d"]
    comparisons: list[dict[str, Any]] = []
    for symbol in symbols:
        item = metrics[symbol]
        comparisons.append(
            {
                "symbol": symbol,
                "role": "stock" if symbol == ticker_symbol else "benchmark" if symbol == args.benchmark.upper() else "sector" if symbol == args.sector.upper() else "peer",
                "date": item["date"],
                "return_1d": item["return_1d"],
                "relative_to_benchmark": number(item["return_1d"] - benchmark_return),
            }
        )

    ticker = yf.Ticker(ticker_symbol)
    news, news_warnings = serialize_news(ticker, ticker_symbol)
    filings, filing_warnings = serialize_filings(ticker)
    warnings = [
        "Yahoo Finance / yfinance is an unofficial research source; verify material claims against primary sources.",
        "News near a price move is context, not proof of causation.",
        *news_warnings,
        *filing_warnings,
    ]

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ticker": ticker_symbol,
        "requested_date": args.date,
        "investigation_date": focus_date,
        "date_selection_note": selection_note,
        "benchmark": args.benchmark.upper(),
        "sector": args.sector.upper(),
        "peers": peers,
        "focus": metrics[ticker_symbol],
        "comparisons": comparisons,
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

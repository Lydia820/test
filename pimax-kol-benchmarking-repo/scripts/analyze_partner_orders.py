#!/usr/bin/env python3
"""Summarize Pimax affiliate orders by month, custom phase, and event windows.

This helper is intentionally descriptive. It does not infer content causality or
map order values to products.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


def parse_date(value: str) -> date | None:
    text = (value or "").strip()
    if not text:
        return None
    normalized = text.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized).date()
    except ValueError:
        pass
    for fmt in ("%Y/%m/%d %H:%M", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def parse_number(value: str) -> float | None:
    text = (value or "").strip().replace(",", "")
    for token in ("$", "€", "£"):
        text = text.replace(token, "")
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def percent_change(current: float, previous: float) -> float | None:
    if previous == 0:
        return None
    return round((current / previous - 1) * 100, 2)


def summarize(rows: list[dict[str, Any]], start: date, end: date) -> dict[str, Any]:
    selected = [row for row in rows if start <= row["date"] <= end]
    values = [row["value"] for row in selected if row["value"] is not None]
    days = (end - start).days + 1
    new_known = [row["new_customer"] for row in selected if row["new_customer"] is not None]
    high_value = [value for value in values if value >= 2100]
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "days": days,
        "orders": len(selected),
        "subtotal": round(sum(values), 2),
        "orders_per_day": round(len(selected) / days, 4),
        "subtotal_per_day": round(sum(values) / days, 2),
        "aov": round(sum(values) / len(values), 2) if values else None,
        "new_customer_share": round(sum(new_known) / len(new_known), 4) if new_known else None,
        "high_value_order_share": round(len(high_value) / len(values), 4) if values else None,
    }


def add_change(current: dict[str, Any], previous: dict[str, Any] | None) -> dict[str, Any]:
    result = dict(current)
    if previous is None:
        result["change_vs_previous"] = None
        return result
    result["change_vs_previous"] = {
        "orders_per_day_pct": percent_change(current["orders_per_day"], previous["orders_per_day"]),
        "subtotal_per_day_pct": percent_change(current["subtotal_per_day"], previous["subtotal_per_day"]),
        "aov_pct": percent_change(current["aov"], previous["aov"])
        if current["aov"] is not None and previous["aov"] is not None
        else None,
        "high_value_share_point_change": round(
            current["high_value_order_share"] - previous["high_value_order_share"], 4
        )
        if current["high_value_order_share"] is not None
        and previous["high_value_order_share"] is not None
        else None,
    }
    return result


def load_json_list(path: str | None) -> list[dict[str, Any]]:
    if not path:
        return []
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Affiliate order CSV")
    parser.add_argument("--name", default="Partner", help="Partner label")
    parser.add_argument("--output", required=True, help="Output JSON")
    parser.add_argument("--date-col", default="Order Date")
    parser.add_argument("--order-col", default="Order Number")
    parser.add_argument("--value-col", default="Order Subtotal")
    parser.add_argument("--status-col", default="Order Status")
    parser.add_argument("--approved-values", default="approved")
    parser.add_argument("--currency-col", default="Currency")
    parser.add_argument("--country-col", default="country")
    parser.add_argument("--new-customer-col", default="New Customer ?")
    parser.add_argument("--conversion-col", default="Conversion Source")
    parser.add_argument("--code-col", default="Discount codes")
    parser.add_argument("--phase-file", help="JSON list with name, start, end")
    parser.add_argument("--events-file", help="JSON list with name, date, optional link")
    parser.add_argument("--windows", default="7,14,21,30")
    args = parser.parse_args()

    approved_values = {item.strip().lower() for item in args.approved_values.split(",") if item.strip()}
    source_path = Path(args.input)
    raw_rows: list[dict[str, str]] = []
    with source_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        required = {args.date_col, args.order_col, args.value_col, args.status_col}
        missing = sorted(required - fields)
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")
        raw_rows = list(reader)

    status_counts = Counter((row.get(args.status_col) or "").strip() or "<blank>" for row in raw_rows)
    approved_raw = [
        row
        for row in raw_rows
        if (row.get(args.status_col) or "").strip().lower() in approved_values
    ]
    seen_ids: set[str] = set()
    duplicate_ids = 0
    rows: list[dict[str, Any]] = []
    invalid_dates = 0
    missing_values = 0
    for index, row in enumerate(approved_raw, start=1):
        order_id = (row.get(args.order_col) or "").strip() or f"<row-{index}>"
        if order_id in seen_ids:
            duplicate_ids += 1
            continue
        seen_ids.add(order_id)
        order_date = parse_date(row.get(args.date_col, ""))
        if order_date is None:
            invalid_dates += 1
            continue
        value = parse_number(row.get(args.value_col, ""))
        if value is None:
            missing_values += 1
        new_text = (row.get(args.new_customer_col) or "").strip().lower()
        new_customer = True if new_text in {"yes", "y", "true", "1"} else False if new_text in {"no", "n", "false", "0"} else None
        rows.append(
            {
                "date": order_date,
                "value": value,
                "new_customer": new_customer,
                "currency": (row.get(args.currency_col) or "").strip() or "<blank>",
                "country": (row.get(args.country_col) or "").strip() or "<blank>",
                "conversion": (row.get(args.conversion_col) or "").strip() or "<blank>",
                "code": (row.get(args.code_col) or "").strip() or "<blank>",
            }
        )

    if not rows:
        raise ValueError("No approved rows with valid dates remain after cleaning")

    first_date = min(row["date"] for row in rows)
    last_date = max(row["date"] for row in rows)
    currencies = Counter(row["currency"] for row in rows)
    countries = Counter(row["country"] for row in rows)
    conversions = Counter(row["conversion"] for row in rows)
    codes = Counter(row["code"] for row in rows)
    values = [row["value"] for row in rows if row["value"] is not None]

    month_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        month_rows[row["date"].strftime("%Y-%m")].append(row)
    monthly: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None
    for month in sorted(month_rows):
        year, month_number = map(int, month.split("-"))
        start = date(year, month_number, 1)
        next_month = date(year + (month_number == 12), 1 if month_number == 12 else month_number + 1, 1)
        end = next_month - timedelta(days=1)
        if month == first_date.strftime("%Y-%m"):
            start = first_date
        if month == last_date.strftime("%Y-%m"):
            end = last_date
        current = summarize(rows, start, end)
        current["month"] = month
        monthly.append(add_change(current, previous))
        previous = current

    phases_output: list[dict[str, Any]] = []
    previous = None
    for phase in load_json_list(args.phase_file):
        start = parse_date(str(phase.get("start", "")))
        end = parse_date(str(phase.get("end", "")))
        if start is None or end is None or end < start:
            raise ValueError(f"Invalid phase: {phase}")
        current = summarize(rows, start, end)
        current["name"] = str(phase.get("name") or f"{start} to {end}")
        phases_output.append(add_change(current, previous))
        previous = current

    windows = sorted({int(item) for item in args.windows.split(",") if item.strip() and int(item) > 0})
    events_output: list[dict[str, Any]] = []
    for event in load_json_list(args.events_file):
        event_date = parse_date(str(event.get("date", "")))
        if event_date is None:
            raise ValueError(f"Invalid event: {event}")
        comparisons = []
        for window in windows:
            pre = summarize(rows, event_date - timedelta(days=window), event_date - timedelta(days=1))
            post = summarize(rows, event_date, event_date + timedelta(days=window - 1))
            comparisons.append(
                {
                    "window_days": window,
                    "pre": pre,
                    "post": post,
                    "post_vs_pre": add_change(post, pre)["change_vs_previous"],
                }
            )
        events_output.append(
            {
                "name": str(event.get("name") or event_date.isoformat()),
                "date": event_date.isoformat(),
                "link": event.get("link"),
                "comparisons": comparisons,
                "warning": "Descriptive timing comparison only; check commercial and market confounders.",
            }
        )

    price_clusters = Counter(round(value) for value in values)
    result = {
        "partner": args.name,
        "source": str(source_path),
        "analysis_period": {"start": first_date.isoformat(), "end": last_date.isoformat()},
        "data_quality": {
            "source_rows": len(raw_rows),
            "approved_rows_before_deduplication": len(approved_raw),
            "approved_unique_valid_date_rows": len(rows),
            "duplicate_order_ids_removed": duplicate_ids,
            "approved_rows_with_invalid_dates_removed": invalid_dates,
            "approved_rows_with_missing_subtotal": missing_values,
            "status_counts": dict(status_counts),
        },
        "summary": summarize(rows, first_date, last_date),
        "currencies": dict(currencies.most_common()),
        "country_coverage": dict(countries.most_common(20)),
        "conversion_sources": dict(conversions.most_common(20)),
        "discount_codes": dict(codes.most_common(20)),
        "top_rounded_subtotal_clusters": [
            {"rounded_subtotal": amount, "orders": count}
            for amount, count in price_clusters.most_common(20)
        ],
        "monthly": monthly,
        "phases": phases_output,
        "event_windows": events_output,
        "method_note": "Approved unique orders; Order Subtotal; unequal windows normalized per day. No product or causal inference.",
    }
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

FX_TO_EUR = {"EUR": 1.0, "USD": 0.9, "GBP": 1.15}

RAW_EVENTS = [
    {
        "event_id": "e1",
        "timestamp": "2026-02-10T10:00:00Z",
        "type": "Purchase",
        "user_id": "u1",
        "product": {"sku": "p1"},
        "amount": "10.00",
        "currency": "EUR",
    },
    {
        "event_id": "e2",
        "ts": 1770724800,  # epoch seconds
        "eventType": "VIEW",
        "user": {"id": "u2"},
        "product_id": "p2",
    },
    {
        "event_id": "e3",
        "timestamp": "2026-02-10T11:00:00Z",
        "type": "purchase",
        "user_id": None,
        "product_id": "p3",
        "amount": 12,
        "currency": "USD",
    },
    {"event_id": "e4", "timestamp": None, "type": "view", "user_id": "u1", "product_id": "p1"},
    {
        "timestamp": "2026-02-10T12:00:00Z",
        "type": "purchase",
        "user_id": "u3",
        "product_id": "p9",
        "amount": 5,
        "currency": "GBP",
    },
    {
        "event_id": "e5",
        "timestamp": "2026-02-10T12:30:00Z",
        "type": "refund",
        "user_id": "u1",
        "product_id": "p1",
        "amount_eur": -10.0,
    },
]

def normalise_events(raw_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Return a list of dicts with schema:
      event_id: str (required)
      user_id: str | None
      ts: ISO-8601 UTC string "YYYY-MM-DDTHH:MM:SSZ" (required)
      event_type: str (lowercase, required)
      product_id: str | None
      amount_eur: float | None

    Rules:
    - Drop events missing event_id or timestamp
    - timestamp may appear as 'timestamp' ISO string or 'ts' epoch seconds
    - event_type may appear as 'type' or 'eventType'
    - user_id may appear as 'user_id' or user: {id: ...}
    - product_id may appear as 'product_id' or product: {sku: ...}
    - amount_eur: if 'amount_eur' exists use it else convert amount+currency via FX_TO_EUR
    - Preserve input order for events kept

    Hint: start with filtering, then field mapping, then amount conversion.
    """
    # TODO: implement
    raise NotImplementedError

# ---------- minimal test harness ----------
def _assert_equal(actual, expected):
    assert actual == expected, f"\nACTUAL:\n{actual}\n\nEXPECTED:\n{expected}\n"

def run_tests():
    got = normalise_events(RAW_EVENTS)

    # Expect drops: e4 (timestamp None), and the event missing event_id
    _assert_equal([e["event_id"] for e in got], ["e1", "e2", "e3", "e5"])

    # event_type normalised
    _assert_equal([e["event_type"] for e in got], ["purchase", "view", "purchase", "refund"])

    # product_id extraction
    _assert_equal([e["product_id"] for e in got], ["p1", "p2", "p3", "p1"])

    # amount conversion
    # e1: 10 EUR -> 10.0
    # e2: no amount -> None
    # e3: 12 USD -> 10.8
    # e5: amount_eur -> -10.0
    _assert_equal([e["amount_eur"] for e in got], [10.0, None, 10.8, -10.0])

    # ts: ISO passthrough and epoch conversion
    # e1: ISO string passed through as-is
    # e2: epoch 1770724800 -> 2026-02-10T12:00:00Z
    # e3: ISO string passed through as-is
    # e5: ISO string passed through as-is
    _assert_equal(
        [e["ts"] for e in got],
        ["2026-02-10T10:00:00Z", "2026-02-10T12:00:00Z", "2026-02-10T11:00:00Z", "2026-02-10T12:30:00Z"],
    )

    print("✅ All tests passed")

if __name__ == "__main__":
    run_tests()

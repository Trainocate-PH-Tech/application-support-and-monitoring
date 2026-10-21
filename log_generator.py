"""Continuously append reproducible practice events to generator.log."""

import json
import random
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


# Change these values before starting a new practice session.
SEED = 42
INTERVAL_SECONDS = 0.5
LOG_FILE = Path("generator.log")


def generate_line(rng, sequence):
    """Return one event; simulated timestamps make seeded runs reproducible."""
    timestamp = datetime(2026, 10, 21, 10, 14, tzinfo=timezone.utc)
    timestamp += timedelta(seconds=rng.randrange(420))
    event = {
        "id": f"G{sequence:08d}",
        "level": rng.choice(("WARN", "ERROR")),
        "env": "prod",
        "service": "checkout",
        "host": rng.choice(("app-01", "app-02")),
        "path": "/checkout",
        "status": rng.choice(("500", "502", "503", "504", "599")),
        "duration_ms": str(rng.choice((2000, 2001, 3500, 9999, 10000, 25000, 100000))),
        "client": "203.0.113.8",
        "request": f"req-{rng.randrange(700, 1000)}",
        "code": rng.choice(("UPSTREAM_TIMEOUT", "DB_DEADLOCK")),
        "message": rng.choice(("payment timeout", "deadlock detected", "retry exhausted")),
    }
    # Mix eligible events with close distractors, including invalid field values.
    if rng.random() < 0.65:
        field, values = rng.choice((
            ("level", ("INFO", "ERRORISH")),
            ("env", ("staging", "production")),
            ("service", ("auth", "worker", "checkout-v2")),
            ("host", ("app-03", "app-010")),
            ("path", ("/health", "/metrics", "/checkout/retry")),
            ("status", ("200", "401", "5000", "50")),
            ("duration_ms", ("0", "120", "1999")),
            ("client", ("203.0.113.80", "203x0x113x8")),
            ("code", ("OK", "DB_DEADLOCK_RETRY", "UPSTREAM_RESET")),
            ("message", ("retry scheduled", "synthetic test event")),
        ))
        event[field] = rng.choice(values)

    stamp = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    style = rng.choices(("key_value", "json", "pipe", "text"), (7, 1, 1, 1))[0]
    if style == "json":
        return json.dumps({"timestamp": stamp, **event})
    if style == "pipe":
        return " | ".join((stamp, *(f"{key}={value}" for key, value in event.items())))
    if style == "text":
        return f"[{stamp}] {event['level']}: {event['service']} - {event['message']} ({event['id']})"
    fields = " ".join(f"{key}={value}" for key, value in event.items() if key != "message")
    return f'{stamp} {fields} message="{event["message"]}"'


def main():
    rng = random.Random(SEED)
    try:
        # Append preserves earlier sessions; line buffering makes tail updates immediate.
        with LOG_FILE.open("a", encoding="utf-8", buffering=1) as log:
            print("Running application...", flush=True)
            sequence = 1
            while True:
                log.write(generate_line(rng, sequence) + "\n")
                sequence += 1
                time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

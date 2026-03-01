"""Python entry points used by the browser WASM worker adapter.

This is intentionally minimal scaffolding so the JS worker protocol can be
wired first. Replace the run_partition implementation with the real search.
"""

from __future__ import annotations

import json
from typing import Any

_STATE: dict[str, Any] = {}


def init_worker(payload_json: str) -> str:
    """Initialize worker-global state.

    Args:
        payload_json: JSON string containing serialized snapshot and pools.
    Returns:
        JSON ack string.
    """
    payload = json.loads(payload_json)
    _STATE["snap"] = payload.get("snap")
    _STATE["pools"] = payload.get("pools")
    _STATE["locked"] = payload.get("locked")
    _STATE["ring_pool"] = payload.get("ring_pool")
    return json.dumps({"ok": True})


def run_partition(payload_json: str) -> str:
    """Run one partition and return a solver_search-compatible result object.

    Current behavior is a stub so integration can be validated before porting
    the full solver logic.
    """
    payload = json.loads(payload_json)
    _partition = payload.get("partition")

    # TODO: Port JS worker enumeration and scoring to python.
    # Return format must match solver_search.js expectations.
    result = {
        "worker_id": payload.get("worker_id"),
        "checked": 0,
        "feasible": 0,
        "top5": [],
    }
    return json.dumps(result)


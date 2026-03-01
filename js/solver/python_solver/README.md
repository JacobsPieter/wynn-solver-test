# Python solver (WASM) scaffolding

This directory contains an experimental worker adapter that allows the existing
solver UI orchestration to talk to Python running in WebAssembly.

## Files

- `worker_adapter.js` — Web Worker entry point used by `solver_search.js` when
  enabled via `?solver_worker=python`.
- `solver_entry.py` — Python entry points called by the worker adapter
  (`init_worker`, `run_partition`).

## Runtime

`worker_adapter.js` uses Pyodide by default:

- default base URL: `https://cdn.jsdelivr.net/pyodide/v0.27.2/full/`
- override with worker query param: `pyodide_url=<base_url>`

## Enabling in the solver

Open the solver page with query parameter:

```text
?solver_worker=python
```

This keeps JS worker behavior as the default and uses Python mode only when
explicitly requested.

## Next step

Port core logic from `js/solver/solver_worker.js` into `solver_entry.py` and
return partition results in the same shape expected by `solver_search.js`:

```json
{
  "checked": 0,
  "feasible": 0,
  "top5": []
}
```


/*
 * Experimental Python/WASM solver worker adapter.
 *
 * Protocol compatibility target: js/solver/solver_search.js
 *  - receives: init / run with { partition, worker_id, ... }
 *  - sends:    progress / done
 *
 * Query params supported on worker URL:
 *  - pyodide_url=<base URL ending with />
 */

let _pyodide = null;
let _pyReady = null;
let _cfg = null;

function _get_query_param(name) {
    try {
        return (new URL(self.location.href)).searchParams.get(name);
    } catch (_e) {
        return null;
    }
}

function _default_pyodide_url() {
    // CDN default; can be overridden by pyodide_url query param.
    return 'https://cdn.jsdelivr.net/pyodide/v0.27.2/full/';
}

async function _load_py_runtime() {
    if (_pyReady) return _pyReady;

    _pyReady = (async () => {
        const baseUrl = _get_query_param('pyodide_url') || _default_pyodide_url();
        importScripts(`${baseUrl}pyodide.js`);
        _pyodide = await loadPyodide({ indexURL: baseUrl });

        // Load the local python entry module from this directory.
        const entryUrl = new URL('./solver_entry.py', self.location.href).toString();
        const entryCode = await (await fetch(entryUrl)).text();

        await _pyodide.runPythonAsync(`
import json
${entryCode}
`);

        return _pyodide;
    })();

    return _pyReady;
}

function _post_done(worker_id, checked = 0, feasible = 0, top5 = []) {
    self.postMessage({
        type: 'done',
        worker_id,
        checked,
        feasible,
        top5,
    });
}

async function _handle_init(msg) {
    _cfg = msg;
    const py = await _load_py_runtime();
    const payload = JSON.stringify({
        snap: msg.snap,
        pools: msg.pools,
        locked: msg.locked,
        ring_pool: msg.ring_pool,
    });

    const init_worker = py.globals.get('init_worker');
    init_worker(payload);

    // Match existing worker UX: periodic progress messages are optional.
    self.postMessage({ type: 'progress', checked: 0, feasible: 0, top5_names: [] });

    // Keep behavior parity with JS worker: init includes first partition.
    if (msg.partition) {
        await _handle_run(msg);
    }
}

async function _handle_run(msg) {
    const py = await _load_py_runtime();
    const run_partition = py.globals.get('run_partition');

    const resultText = run_partition(JSON.stringify({
        partition: msg.partition,
        worker_id: msg.worker_id,
    }));

    let result = null;
    try {
        result = JSON.parse(resultText);
    } catch (_e) {
        result = null;
    }

    if (!result || typeof result !== 'object') {
        _post_done(msg.worker_id, 0, 0, []);
        return;
    }

    _post_done(
        msg.worker_id,
        result.checked ?? 0,
        result.feasible ?? 0,
        Array.isArray(result.top5) ? result.top5 : []
    );
}

self.onmessage = async (e) => {
    const msg = e.data || {};
    try {
        if (msg.type === 'init') {
            await _handle_init(msg);
            return;
        }
        if (msg.type === 'run') {
            await _handle_run(msg);
            return;
        }
    } catch (err) {
        console.error('[solver/python_worker] error:', err);
        // Ensure orchestrator does not hang if this partition fails.
        _post_done(msg.worker_id, 0, 0, []);
    }
};

import io
import threading
import atexit
from contextlib import redirect_stdout, redirect_stderr

from flask import Flask, request, redirect, url_for, render_template, jsonify

import configs.PT5801 as CONFIG
from web_runner_PT5801 import run_cycles
from web_runner_PT7526_RPT import run_rpt
from core import cycler_middle_server


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.after_request
def _no_cache(resp):
    resp.headers['Cache-Control'] = 'no-store'
    return resp


@app.get("/")
def index():
    return render_template(
        "index.html",
        available_banks=CONFIG.AVAILABLE_BANKS,
        active_job_id=None,
    )


@app.post("/run")
def start_run():
    try:
        bank = int(request.form.get("bank_request", "").strip())
        skip_csv = request.form.get("specimens_to_skip", "").strip()
        cycles = int(request.form.get("cycles_to_complete", "").strip())
    except Exception:
        return "Invalid parameters", 400

    # Synchronous execution, capture logs and render when complete
    buf = io.StringIO()
    status = "done"
    try:
        with redirect_stdout(buf), redirect_stderr(buf):
            run_cycles(bank_request=bank, cycles_to_complete=cycles, specimens_to_skip_csv=skip_csv)
    except Exception as e:
        status = "error"
        buf.write(f"\n[ERROR] {repr(e)}\n")
    logs = buf.getvalue()
    return render_template("logs.html", job_id="sync", status=status, logs=logs, middle_server_events="")


@app.post("/run_7526_rpt")
def start_run_7526_rpt():
    banks_text = (request.form.get("banks", "") or "").strip()
    if not banks_text:
        return "Banks input required (use ALL or comma-separated list)", 400
    skip_csv = (request.form.get("specimens_to_skip", "") or "").strip()

    buf = io.StringIO()
    status = "done"
    try:
        with redirect_stdout(buf), redirect_stderr(buf):
            run_rpt(banks_input=banks_text, specimens_to_skip_csv=skip_csv)
    except Exception as e:
        status = "error"
        buf.write(f"\n[ERROR] {repr(e)}\n")
    logs = buf.getvalue()
    return render_template("logs.html", job_id="sync", status=status, logs=logs, middle_server_events="")

@app.get("/logs/<job_id>")
def logs(job_id: str):
    return render_template("logs.html", job_id=job_id, status="n/a", logs="No background jobs; synchronous mode only.", middle_server_events="")


@app.post("/api/run_7526_rpt")
def api_run_7526_rpt():
    data = request.get_json(silent=True) or {}
    banks_text = (data.get("banks", "") or "").strip()
    if not banks_text:
        return jsonify({"status": "error", "error": "Banks input required (use ALL or comma-separated list)"}), 400
    skip_csv = (data.get("specimens_to_skip", "") or "").strip()

    buf = io.StringIO()
    status = "done"
    try:
        with redirect_stdout(buf), redirect_stderr(buf):
            run_rpt(banks_input=banks_text, specimens_to_skip_csv=skip_csv)
    except Exception as e:
        status = "error"
        buf.write(f"\n[ERROR] {repr(e)}\n")
    logs = buf.getvalue()
    return jsonify({"status": status, "logs": logs})


@app.get("/api/middle_server_events")
def api_middle_server_events():
    try:
        events = cycler_middle_server.get_debug_events()
    except Exception:
        events = []
    # Return last 200 for brevity
    return jsonify({"events": events[-200:]})


if __name__ == "__main__":
    # Start the middle server and ensure it stops when app exits
    t = threading.Thread(target=cycler_middle_server.start_server, daemon=True)
    t.start()
    atexit.register(cycler_middle_server.stop_server)

    # Run Flask app; ensure single-process (no reloader) so the TCP thread starts once
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)



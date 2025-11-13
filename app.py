# app.py
import threading
from flask import Flask, render_template_string, request, jsonify
import pyvisa
from datetime import datetime

app = Flask(__name__)

# ----------------------------------------------------------------------
# Global state (protected by a lock because Flask can serve multiple requests)
# ----------------------------------------------------------------------
state_lock = threading.Lock()
instrument = None          # the active pyvisa instrument
log_lines = []            # list of (timestamp, message) tuples
command_history = []      # last 20 commands

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def log(msg: str):
    """Append a timestamped message to the log (thread-safe)."""
    ts = datetime.now().strftime("%H:%M:%S")
    with state_lock:
        log_lines.append((ts, msg))
        # keep only the last 200 lines
        if len(log_lines) > 200:
            log_lines.pop(0)

def get_instrument():
    """Return the current instrument or raise an exception."""
    if instrument is None:
        raise RuntimeError("No device connected.")
    return instrument

# ----------------------------------------------------------------------
# HTML template (embedded – no extra files needed)
# ----------------------------------------------------------------------
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>GPIB Web Manager</title>
  <style>
    body {font-family: Arial, sans-serif; margin: 20px; background:#f7f7f7;}
    .box {background:#fff; padding:15px; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.1); margin-bottom:15px;}
    input, button, select {margin:5px 0; padding:6px; font-size:1em;}
    button {background:#0069d9; color:#fff; border:none; border-radius:4px; cursor:pointer;}
    button:hover {background:#0053a6;}
    .log {max-height:300px; overflow-y:auto; background:#eee; padding:10px; border-radius:4px; font-family:monospace;}
    .history {max-height:150px; overflow-y:auto; background:#fafafa; padding:5px; border:1px solid #ddd; border-radius:4px;}
  </style>
</head>
<body>
  <h1>GPIB Device Manager</h1>

  <div class="box">
    <h3>1. Connect</h3>
    <form id="connectForm">
      GPIB address: <input type="text" name="address" value="1" size="4">
      <button type="submit">Connect</button>
      <span id="connStatus"></span>
    </form>
  </div>

  <div class="box">
    <h3>2. Send Command</h3>
    <form id="sendForm">
      <select id="historySelect" onchange="fillCommand(this.value)">
        <option value="">-- or pick from history --</option>
        {% for cmd in history %}
        <option>{{ cmd }}</option>
        {% endfor %}
      </select><br>
      Command: <input type="text" id="cmdInput" name="command" size="40" placeholder="*IDN?">
      <button type="submit">Send</button>
      <button type="button" onclick="clearResponse()">Clear</button>
    </form>
    <pre id="response" style="background:#fff; border:1px solid #ccc; padding:8px; min-height:60px;"></pre>
  </div>

  <div class="box">
    <h3>Log</h3>
    <div class="log" id="log"></div>
    <button onclick="document.getElementById('log').innerHTML=''">Clear Log</button>
  </div>

  <script>
    // ------------------------------------------------------------------
    // Helper to update UI from JSON responses
    // ------------------------------------------------------------------
    function updateUI(data) {
      if (data.log) {
        const logDiv = document.getElementById('log');
        data.log.forEach(line => {
          logDiv.innerHTML += `<div>[${line[0]}] ${line[1]}</div>`;
        });
        logDiv.scrollTop = logDiv.scrollHeight;
      }
      if (data.history) {
        const sel = document.getElementById('historySelect');
        sel.innerHTML = '<option value="">-- or pick from history --</option>';
        data.history.forEach(c => {
          const opt = document.createElement('option');
          opt.text = c; sel.add(opt);
        });
      }
      if (data.response !== undefined) {
        document.getElementById('response').textContent = data.response;
      }
      if (data.status) {
        document.getElementById('connStatus').textContent = data.status;
      }
    }

    // ------------------------------------------------------------------
    // Connect form
    // ------------------------------------------------------------------
    document.getElementById('connectForm').onsubmit = async e => {
      e.preventDefault();
      const addr = e.target.address.value.trim();
      const r = await fetch('/connect', {method:'POST', body:new FormData(e.target)});
      const data = await r.json();
      updateUI(data);
    };

    // ------------------------------------------------------------------
    // Send command form
    // ------------------------------------------------------------------
    document.getElementById('sendForm').onsubmit = async e => {
      e.preventDefault();
      const cmd = document.getElementById('cmdInput').value.trim();
      if (!cmd) return;
      const form = new FormData();
      form.append('command', cmd);
      const r = await fetch('/send', {method:'POST', body:form});
      const data = await r.json();
      updateUI(data);
    };

    function fillCommand(val) {
      if (val) document.getElementById('cmdInput').value = val;
    }
    function clearResponse() {
      document.getElementById('response').textContent = '';
    }

    // ------------------------------------------------------------------
    // Auto-refresh log & history every 2 seconds
    // ------------------------------------------------------------------
    setInterval(async () => {
      const r = await fetch('/status');
      const data = await r.json();
      updateUI(data);
    }, 2000);
  </script>
</body>
</html>
"""

# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------
@app.route("/")
def index():
    with state_lock:
        return render_template_string(
            HTML_TEMPLATE,
            history=reversed(command_history[-20:])   # newest on top
        )

@app.route("/connect", methods=["POST"])
def connect():
    address = request.form.get("address", "").strip()
    global instrument
    try:
        rm = pyvisa.ResourceManager()
        instr = rm.open_resource(f"GPIB::{address}::INSTR")
        with state_lock:
            instrument = instr
        log(f"Connected to GPIB::{address}")
        return jsonify(
            status=f"Connected to GPIB::{address}",
            log=log_lines[-10:],        # last 10 lines
            history=command_history
        )
    except Exception as e:
        log(f"Connect error: {e}")
        return jsonify(
            status="Error",
            log=log_lines[-10:],
            history=command_history
        ), 500

@app.route("/send", methods=["POST"])
def send():
    cmd = request.form.get("command", "").strip()
    if not cmd:
        return jsonify(response="Empty command"), 400

    try:
        instr = get_instrument()
        instr.write(cmd)
        # Many instruments need a short delay before reading
        instr.read_timeout = 5000   # ms
        resp = instr.read()
        # store in history (dedup)
        with state_lock:
            if cmd not in command_history:
                command_history.append(cmd)
                if len(command_history) > 50:
                    command_history.pop(0)
        log(f"> {cmd}")
        log(f"< {resp}")
        return jsonify(
            response=resp,
            log=log_lines[-10:],
            history=command_history
        )
    except Exception as e:
        log(f"Send error: {e}")
        return jsonify(
            response=f"Error: {e}",
            log=log_lines[-10:],
            history=command_history
        ), 500

@app.route("/status")
def status():
    """Called periodically by the browser to refresh log/history."""
    with state_lock:
        return jsonify(
            log=log_lines[-50:],
            history=command_history,
            status="Connected" if instrument else "Not connected"
        )

# ----------------------------------------------------------------------
# Optional: simple password protection (change SECRET_PASSWORD)
# ----------------------------------------------------------------------
SECRET_PASSWORD = ""   # set to something non-empty if you want a login

@app.before_request
def check_password():
    if SECRET_PASSWORD and request.path != "/login":
        auth = request.authorization
        if not auth or auth.password != SECRET_PASSWORD:
            return ("Unauthorized", 401, {'WWW-Authenticate': 'Basic realm="GPIB"'})

# ----------------------------------------------------------------------
# Run the server
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Debug=True gives auto-reload; change host/port as needed
    app.run(host="127.0.0.1", port=5000, debug=True)
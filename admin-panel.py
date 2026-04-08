#!/usr/bin/env python3
"""
Web Admin Panel - Complete Management Interface
Manage everything from browser
"""

import http.server
import sqlite3
import os
import json
import datetime
import subprocess

DB_PATH = os.path.expanduser("~/my-database.db")
ADMIN_PORT = 9090

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def run_command(cmd):
    """Run system command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return str(e)

def render_admin():
    conn = get_db()
    c = conn.cursor()
    
    # Stats
    stats = {}
    for t in ['users', 'notes', 'projects', 'tasks']:
        c.execute(f"SELECT COUNT(*) FROM {t}")
        stats[t] = c.fetchone()[0]
    
    # Running services
    services = []
    for proc, port in [('dashboard', 8888), ('db-api-server', 3000), ('auto-backup', None)]:
        running = bool(run_command(f"pgrep -f {proc}"))
        services.append({'name': proc, 'port': port or '-', 'status': '✅' if running else '❌'})
    
    # Recent activity
    c.execute("SELECT * FROM tasks ORDER BY id DESC LIMIT 10")
    tasks = [dict(r) for r in c.fetchall()]
    
    conn.close()
    
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Admin Panel</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: monospace; background: #000; color: #0f0; padding: 20px; }}
h1 {{ color: #0f0; margin-bottom: 20px; border-bottom: 1px solid #0f0; padding-bottom: 10px; }}
h2 {{ color: #0f0; margin: 20px 0 10px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }}
.card {{ background: #111; border: 1px solid #0f0; padding: 15px; border-radius: 5px; text-align: center; }}
.card .val {{ font-size: 2.5em; }}
.card .lbl {{ color: #0a0; }}
table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
th {{ color: #0a0; text-align: left; padding: 8px; border-bottom: 1px solid #0f0; }}
td {{ padding: 8px; border-bottom: 1px solid #030; }}
.btn {{ background: #0f0; color: #000; border: none; padding: 10px 20px; margin: 5px; cursor: pointer; font-family: monospace; font-weight: bold; }}
.btn:hover {{ background: #0a0; }}
.log {{ background: #111; border: 1px solid #0f0; padding: 15px; max-height: 300px; overflow-y: auto; font-size: 0.85em; }}
.actions {{ margin: 20px 0; }}
</style></head><body>
<h1>🔧 ADMIN PANEL</h1>
<p>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

<div class="grid">
<div class="card"><div class="val">{stats['users']}</div><div class="lbl">Users</div></div>
<div class="card"><div class="val">{stats['notes']}</div><div class="lbl">Notes</div></div>
<div class="card"><div class="val">{stats['projects']}</div><div class="lbl">Projects</div></div>
<div class="card"><div class="val">{stats['tasks']}</div><div class="lbl">Tasks</div></div>
</div>

<h2>⚡ Services</h2>
<table>
<tr><th>Service</th><th>Port</th><th>Status</th></tr>
{''.join(f"<tr><td>{s['name']}</td><td>{s['port']}</td><td>{s['status']}</td></tr>" for s in services)}
</table>

<h2>📋 Recent Tasks</h2>
<table>
<tr><th>ID</th><th>Title</th><th>Priority</th><th>Done</th></tr>
{''.join(f"<tr><td>{t['id']}</td><td>{t['title']}</td><td>{t['priority']}</td><td>{'✅' if t['done'] else '⬜'}</td></tr>" for t in tasks)}
</table>

<h2>🎮 Actions</h2>
<div class="actions">
<button class="btn" onclick="fetch('/api/backup')">💾 Backup</button>
<button class="btn" onclick="fetch('/api/optimize')">⚡ Optimize</button>
<button class="btn" onclick="fetch('/api/export')">📤 Export</button>
<button class="btn" onclick="fetch('/api/restart')">🔄 Restart Services</button>
</div>

<h2>📝 System Log</h2>
<div class="log" id="log">Loading...</div>

<script>
async function loadLog() {{
    const r = await fetch('/api/log');
    const t = await r.text();
    document.getElementById('log').textContent = t;
}}
loadLog();
setInterval(loadLog, 5000);
</script>
</body></html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(render_admin().encode())
        elif self.path == '/api/backup':
            out = run_command("bash ~/backup-db.sh")
            self.send_json({"ok": True, "output": out})
        elif self.path == '/api/optimize':
            out = run_command("python3 ~/auto-optimizer.py")
            self.send_json({"ok": True, "output": out})
        elif self.path == '/api/export':
            out = run_command("python3 ~/analytics.py")
            self.send_json({"ok": True, "output": out})
        elif self.path == '/api/log':
            if os.path.exists(os.path.expanduser("~/system.log")):
                with open(os.path.expanduser("~/system.log")) as f:
                    log = f.read()[-2000:]
            else:
                log = "No logs yet"
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(log.encode())
        else:
            self.send_error(404)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, *args):
        pass

if __name__ == '__main__':
    print(f"\n  🔧 Admin Panel")
    print(f"  http://localhost:{ADMIN_PORT}")
    print(f"  Press Ctrl+C to stop\n")
    server = http.server.HTTPServer(('0.0.0.0', ADMIN_PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

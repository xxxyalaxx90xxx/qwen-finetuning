#!/usr/bin/env python3
"""Database Web Dashboard - Zero dependencies, works on Termux/Android"""

import http.server
import sqlite3
import json
import os
import datetime

DB_PATH = os.path.expanduser("~/my-database.db")
PORT = 8888

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_stats():
    conn = get_db()
    c = conn.cursor()
    stats = {}
    for t in ["users", "notes", "projects", "tasks"]:
        c.execute(f"SELECT COUNT(*) FROM {t}")
        stats[t] = c.fetchone()[0]
    stats["size"] = os.path.getsize(DB_PATH) // 1024
    conn.close()
    return stats

def render_table(name, columns, rows):
    html = "<table><tr>"
    for col in columns:
        html += f"<th>{col}</th>"
    html += "</tr>"
    for row in rows:
        html += "<tr>"
        for val in row:
            html += f"<td>{val}</td>"
        html += "</tr>"
    html += "</table>"
    return html

def page():
    stats = get_stats()
    conn = get_db()
    c = conn.cursor()
    
    # Users
    c.execute("SELECT * FROM users ORDER BY id")
    users_html = render_table("users", ["ID","Username","Email","Created"],
        [(r["id"], r["username"], r["email"] or "", r["created_at"]) for r in c.fetchall()])
    
    # Notes
    c.execute("SELECT id, title, content, created_at FROM notes ORDER BY id DESC")
    notes_html = render_table("notes", ["ID","Title","Content","Created"],
        [(r["id"], r["title"], (r["content"] or "")[:60], r["created_at"]) for r in c.fetchall()])
    
    # Projects
    c.execute("SELECT * FROM projects ORDER BY id")
    projects_html = render_table("projects", ["ID","Name","Description","Status","Created"],
        [(r["id"], r["name"], r["description"] or "", r["status"], r["created_at"]) for r in c.fetchall()])
    
    # Tasks
    c.execute("SELECT * FROM tasks ORDER BY priority DESC, id")
    tasks_html = render_table("tasks", ["ID","Title","Done","Priority","Created"],
        [(r["id"], r["title"], "Done" if r["done"] else "Pending", r["priority"], r["created_at"]) for r in c.fetchall()])
    
    conn.close()
    
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DB Dashboard</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:sans-serif; background:#111; color:#eee; padding:20px; }}
h1 {{ color:#0af; margin-bottom:10px; }}
p {{ color:#888; }}
.stats {{ display:flex; gap:15px; flex-wrap:wrap; margin:20px 0; }}
.stat {{ background:#1a1a2e; padding:20px; border-radius:10px; text-align:center; min-width:120px; }}
.stat .n {{ font-size:2em; color:#0af; }}
.section {{ background:#1a1a2e; padding:20px; border-radius:10px; margin:15px 0; }}
.section h2 {{ color:#0af; margin-bottom:15px; }}
table {{ width:100%; border-collapse:collapse; }}
th {{ text-align:left; padding:10px; color:#888; border-bottom:1px solid #333; }}
td {{ padding:10px; border-bottom:1px solid #222; }}
.btn {{ background:#0af; color:#000; border:none; padding:8px 16px; border-radius:5px; cursor:pointer; margin:5px; }}
</style></head><body>
<h1>Database Dashboard</h1>
<p>{DB_PATH} | {now}</p>
<div class="stats">
<div class="stat"><div class="n">{stats['users']}</div>Users</div>
<div class="stat"><div class="n">{stats['notes']}</div>Notes</div>
<div class="stat"><div class="n">{stats['projects']}</div>Projects</div>
<div class="stat"><div class="n">{stats['tasks']}</div>Tasks</div>
<div class="stat"><div class="n">{stats['size']}KB</div>Size</div>
</div>
<div class="section"><h2>Users</h2>{users_html}</div>
<div class="section"><h2>Notes</h2>{notes_html}</div>
<div class="section"><h2>Projects</h2>{projects_html}</div>
<div class="section"><h2>Tasks</h2>{tasks_html}</div>
</body></html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(page().encode())
        elif self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(get_stats()).encode())
        elif self.path == '/api/export':
            conn = get_db()
            data = {}
            for t in ['users','notes','projects','tasks']:
                c = conn.cursor()
                c.execute(f"SELECT * FROM {t}")
                data[t] = [dict(r) for r in c.fetchall()]
            conn.close()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data, indent=2, default=str).encode())
        else:
            self.send_error(404)
    
    def log_message(self, *args):
        pass

if __name__ == '__main__':
    print(f"\n  Database Dashboard")
    print(f"  http://localhost:{PORT}")
    print(f"  http://127.0.0.1:{PORT}")
    print(f"  Press Ctrl+C to stop\n")
    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

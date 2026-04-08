#!/usr/bin/env python3
"""
Advanced Dashboard v2.0 with Themes, Real-time Stats, and AI Insights
"""

import http.server
import sqlite3
import os
import json
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
    c.execute("SELECT COUNT(*) FROM tasks WHERE done=1")
    stats['done'] = c.fetchone()[0]
    stats['size'] = os.path.getsize(DB_PATH) // 1024
    conn.close()
    return stats

def render_dashboard():
    stats = get_stats()
    conn = get_db()
    c = conn.cursor()
    
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Recent tasks
    c.execute("SELECT * FROM tasks ORDER BY priority DESC, id LIMIT 10")
    tasks_html = ""
    for r in c.fetchall():
        status = "✅" if r["done"] else "⬜"
        pri_bar = "🔴" * r["priority"] + "⚪" * (5 - r["priority"])
        tasks_html += f"<tr><td>{r['id']}</td><td>{status}</td><td>{r['title']}</td><td>{pri_bar}</td><td>{r['created_at']}</td></tr>"
    
    # Recent notes
    c.execute("SELECT * FROM notes ORDER BY id DESC LIMIT 10")
    notes_html = ""
    for r in c.fetchall():
        content_preview = (r["content"] or "")[:80]
        notes_html += f"<tr><td>{r['id']}</td><td>{r['title']}</td><td>{content_preview}</td><td>{r['created_at']}</td></tr>"
    
    # Projects
    c.execute("SELECT p.*, COUNT(t.id) as task_count FROM projects p LEFT JOIN tasks t ON p.id = t.project_id GROUP BY p.id")
    projects_html = ""
    for r in c.fetchall():
        projects_html += f"<tr><td>{r['id']}</td><td>{r['name']}</td><td>{r['description'] or '-'}</td><td><span class='badge'>{r['status']}</span></td><td>{r['task_count']}</td></tr>"
    
    # AI Insights
    completion_rate = int(stats['done'] / max(stats['tasks'], 1) * 100)
    insights = []
    if completion_rate >= 80:
        insights.append("🌟 Excellent completion rate!")
    elif completion_rate < 50:
        insights.append("⚠️ Low completion - focus on tasks")
    
    c.execute("SELECT COUNT(*) FROM tasks WHERE priority >= 4 AND done=0")
    high_pri = c.fetchone()[0]
    if high_pri > 0:
        insights.append(f"🔴 {high_pri} high-priority tasks pending")
    
    insights_html = "".join(f"<div class='insight'>{i}</div>" for i in insights)
    
    conn.close()
    
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DB Dashboard v2.0</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system, sans-serif; background: #0a0a0f; color: #e0e0e0; }}
.container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
header {{ background: linear-gradient(135deg, #0f0f23, #1a1a3e); padding: 25px; border-radius: 16px; margin-bottom: 20px; border: 1px solid #333; }}
header h1 {{ font-size: 2em; color: #00d4ff; text-shadow: 0 0 20px rgba(0,212,255,0.3); }}
header p {{ color: #888; margin-top: 5px; }}
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 20px; }}
.stat {{ background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 25px; border-radius: 12px; text-align: center; border: 1px solid #333; }}
.stat .num {{ font-size: 3em; font-weight: bold; background: linear-gradient(45deg, #00d4ff, #7b2cbf); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.stat .label {{ color: #888; margin-top: 5px; font-size: 0.9em; }}
.section {{ background: #1a1a2e; border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid #333; }}
.section h2 {{ color: #00d4ff; margin-bottom: 15px; font-size: 1.3em; }}
table {{ width: 100%; border-collapse: collapse; font-size: 0.9em; }}
th {{ text-align: left; padding: 12px 10px; color: #888; border-bottom: 2px solid #333; }}
td {{ padding: 10px; border-bottom: 1px solid #222; }}
tr:hover {{ background: #222; }}
.badge {{ padding: 4px 10px; border-radius: 6px; background: #004d00; color: #00ff00; font-size: 0.85em; }}
.insights {{ background: linear-gradient(135deg, #1a1a3e, #2d1b69); padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #7b2cbf; }}
.insights h2 {{ color: #a78bfa; }}
.insight {{ padding: 10px; margin: 8px 0; background: rgba(123,44,191,0.2); border-radius: 8px; border-left: 4px solid #7b2cbf; }}
.refresh {{ position: fixed; bottom: 20px; right: 20px; background: #00d4ff; color: #000; border: none; padding: 15px 25px; border-radius: 50px; cursor: pointer; font-weight: bold; font-size: 1em; box-shadow: 0 4px 15px rgba(0,212,255,0.3); }}
.refresh:hover {{ background: #00b8e6; }}
</style>
<meta http-equiv="refresh" content="30">
</head><body>
<div class="container">
<header>
<h1>📊 Database Dashboard v2.0</h1>
<p>{DB_PATH.split('/')[-1]} | {now} | Auto-refresh: 30s</p>
</header>

<div class="stats">
<div class="stat"><div class="num">{stats['users']}</div><div class="label">👤 Users</div></div>
<div class="stat"><div class="num">{stats['notes']}</div><div class="label">📝 Notes</div></div>
<div class="stat"><div class="num">{stats['projects']}</div><div class="label">📁 Projects</div></div>
<div class="stat"><div class="num">{stats['tasks']}</div><div class="label">✅ Tasks</div></div>
<div class="stat"><div class="num">{stats['done']}</div><div class="label">✓ Done</div></div>
<div class="stat"><div class="num">{stats['size']}</div><div class="label">💾 KB</div></div>
</div>

<div class="insights">
<h2>🤖 AI Insights</h2>
{insights_html if insights_html else '<div class="insight">✅ System running optimally</div>'}
</div>

<div class="section">
<h2>📋 Tasks (Priority Sorted)</h2>
<table>
<tr><th>ID</th><th>Status</th><th>Title</th><th>Priority</th><th>Created</th></tr>
{tasks_html}
</table>
</div>

<div class="section">
<h2>📝 Recent Notes</h2>
<table>
<tr><th>ID</th><th>Title</th><th>Content</th><th>Created</th></tr>
{notes_html}
</table>
</div>

<div class="section">
<h2>📁 Projects</h2>
<table>
<tr><th>ID</th><th>Name</th><th>Description</th><th>Status</th><th>Tasks</th></tr>
{projects_html}
</table>
</div>
</div>

<button class="refresh" onclick="location.reload()">🔄 Refresh</button>
</body></html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(render_dashboard().encode())
        elif self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(get_stats()).encode())
        else:
            self.send_error(404)
    
    def log_message(self, *args):
        pass

if __name__ == '__main__':
    print(f"\n  📊 Dashboard v2.0")
    print(f"  http://localhost:{PORT}")
    print(f"  Auto-refresh: every 30s")
    print(f"  Press Ctrl+C to stop\n")
    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

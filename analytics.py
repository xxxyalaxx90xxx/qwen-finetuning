#!/usr/bin/env python3
"""
Analytics & Reports Module
Generates comprehensive reports and insights from database
"""

import sqlite3
import os
import json
import datetime

DB_PATH = os.path.expanduser("~/my-database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def generate_report():
    """Generate full analytics report"""
    print("\n" + "="*50)
    print("  📊 ANALYTICS & REPORTS")
    print("="*50)
    
    conn = get_db()
    c = conn.cursor()
    
    # 1. Overview
    print("\n📋 OVERVIEW")
    print("-"*30)
    for t in ['users', 'notes', 'projects', 'tasks']:
        c.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"  {t:<12}: {c.fetchone()[0]}")
    print(f"  {'DB Size':<12}: {os.path.getsize(DB_PATH)//1024} KB")
    
    # 2. Users Analysis
    print("\n👤 USERS ANALYSIS")
    print("-"*30)
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE created_at >= date('now', '-7 days')")
    new_week = c.fetchone()[0]
    print(f"  Total users:     {total}")
    print(f"  New this week:   {new_week}")
    
    # 3. Notes Analysis
    print("\n📝 NOTES ANALYSIS")
    print("-"*30)
    c.execute("SELECT COUNT(*) FROM notes")
    total = c.fetchone()[0]
    c.execute("SELECT AVG(LENGTH(content)) FROM notes WHERE content IS NOT NULL")
    avg_len = c.fetchone()[0] or 0
    c.execute("SELECT title, LENGTH(content) as len FROM notes ORDER BY len DESC LIMIT 3")
    longest = c.fetchall()
    print(f"  Total notes:     {total}")
    print(f"  Avg length:      {int(avg_len)} chars")
    print(f"  Longest notes:")
    for n in longest:
        print(f"    - {n['title']}: {n['len']} chars")
    
    # 4. Tasks Analysis
    print("\n✅ TASKS ANALYSIS")
    print("-"*30)
    c.execute("SELECT COUNT(*) FROM tasks WHERE done=1")
    done = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tasks WHERE done=0")
    pending = c.fetchone()[0]
    total = done + pending
    c.execute("SELECT AVG(priority) FROM tasks")
    avg_pri = c.fetchone()[0] or 0
    c.execute("SELECT title, priority FROM tasks ORDER BY priority DESC LIMIT 3")
    top = c.fetchall()
    
    print(f"  Total tasks:     {total}")
    print(f"  Completed:       {done} ({int(done/max(total,1)*100)}%)")
    print(f"  Pending:         {pending} ({int(pending/max(total,1)*100)}%)")
    print(f"  Avg priority:    {avg_pri:.1f}/5")
    print(f"  Highest priority:")
    for t in top:
        print(f"    🔴 {t['title']} (P{t['priority']})")
    
    # 5. Projects Analysis
    print("\n📁 PROJECTS ANALYSIS")
    print("-"*30)
    c.execute("SELECT p.name, p.status, COUNT(t.id) as tasks FROM projects p LEFT JOIN tasks t ON p.id = t.project_id GROUP BY p.id")
    for p in c.fetchall():
        print(f"  {p['name']}: {p['status']}, {p['tasks']} tasks")
    
    # 6. Activity Timeline
    print("\n📈 ACTIVITY TIMELINE")
    print("-"*30)
    c.execute("""
        SELECT DATE(created_at) as day, COUNT(*) as count
        FROM (
            SELECT created_at FROM users
            UNION ALL SELECT created_at FROM notes
            UNION ALL SELECT created_at FROM tasks
        )
        GROUP BY day ORDER BY day DESC LIMIT 7
    """)
    for row in c.fetchall():
        bar = "█" * row['count']
        print(f"  {row['day']}: {bar} ({row['count']})")
    
    conn.close()

def export_report_json():
    """Export full report as JSON"""
    conn = get_db()
    c = conn.cursor()
    
    report = {
        "generated": datetime.datetime.now().isoformat(),
        "summary": {},
        "tasks": {},
        "users": {},
    }
    
    for t in ['users', 'notes', 'projects', 'tasks']:
        c.execute(f"SELECT COUNT(*) FROM {t}")
        report['summary'][t] = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM tasks WHERE done=1")
    report['tasks']['completed'] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tasks WHERE done=0")
    report['tasks']['pending'] = c.fetchone()[0]
    
    conn.close()
    
    filename = os.path.expanduser("~/report.json")
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Report exported to {filename}")

def export_html_report():
    """Generate HTML report"""
    conn = get_db()
    c = conn.cursor()
    
    html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>DB Report</title>
<style>
body { font-family: sans-serif; background: #111; color: #eee; padding: 20px; }
h1 { color: #0af; } h2 { color: #0af; border-bottom: 1px solid #333; padding-bottom: 10px; }
table { width: 100%; border-collapse: collapse; margin: 15px 0; }
th { text-align: left; padding: 10px; color: #888; border-bottom: 1px solid #333; }
td { padding: 10px; border-bottom: 1px solid #222; }
.badge { padding: 3px 8px; border-radius: 5px; }
.done { background: #004d00; color: #0f0; }
.pending { background: #4d3300; color: #fa0; }
</style></head><body>
<h1>📊 Database Report</h1>
<p>""" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + """</p>"""
    
    for table in ['users', 'notes', 'projects', 'tasks']:
        c.execute(f"SELECT * FROM {table}")
        rows = c.fetchall()
        cols = [d[0] for d in c.description]
        
        html += f"<h2>{table.title()} ({len(rows)})</h2><table><tr>"
        for col in cols:
            html += f"<th>{col}</th>"
        html += "</tr>"
        for r in rows:
            html += "<tr>"
            for val in r:
                html += f"<td>{val}</td>"
            html += "</tr>"
        html += "</table>"
    
    conn.close()
    html += "</body></html>"
    
    filename = os.path.expanduser("~/report.html")
    with open(filename, 'w') as f:
        f.write(html)
    
    print(f"✅ HTML report: {filename}")

if __name__ == "__main__":
    generate_report()
    export_report_json()
    export_html_report()

#!/usr/bin/env python3
"""
New Features for Database System
1. CSV Import/Export
2. Global Search
3. Logging System
4. Task Reminders
5. Data Visualization (ASCII charts)
"""

import sqlite3
import os
import csv
import json
import datetime

DB_PATH = os.path.expanduser("~/my-database.db")
LOG_PATH = os.path.expanduser("~/system.log")

# ═══════════════════════════════════════════
# Feature 1: CSV Import/Export
# ═══════════════════════════════════════════

def export_csv(table_name):
    """Export a table to CSV"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table_name}")
    rows = c.fetchall()
    cols = [d[0] for d in c.description]
    
    filename = os.path.expanduser(f"~/{table_name}.csv")
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(cols)
        writer.writerows(rows)
    
    conn.close()
    print(f"✅ Exported {len(rows)} rows to {filename}")
    return filename

def import_csv(table_name, csv_file):
    """Import data from CSV into a table"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        count = 0
        for row in reader:
            placeholders = ','.join(['?' for _ in row])
            c.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", row)
            count += 1
    
    conn.commit()
    conn.close()
    print(f"✅ Imported {count} rows from {csv_file}")

def export_all_csv():
    """Export all tables to CSV"""
    for table in ['users', 'notes', 'projects', 'tasks']:
        export_csv(table)
    print("✅ All tables exported to CSV")

# ═══════════════════════════════════════════
# Feature 2: Global Search
# ═══════════════════════════════════════════

def global_search(query):
    """Search across all tables"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    results = {}
    tables = {
        'users': ['username', 'email'],
        'notes': ['title', 'content', 'tags'],
        'projects': ['name', 'description'],
        'tasks': ['title']
    }
    
    for table, cols in tables.items():
        conditions = ' OR '.join([f"{c} LIKE ?" for c in cols])
        params = [f'%{query}%'] * len(cols)
        c.execute(f"SELECT * FROM {table} WHERE {conditions}", params)
        rows = c.fetchall()
        if rows:
            results[table] = [dict(r) for r in rows]
    
    conn.close()
    
    if not results:
        print(f"🔍 No results for '{query}'")
        return
    
    print(f"🔍 Found results for '{query}':\n")
    for table, rows in results.items():
        print(f"  📂 {table} ({len(rows)} matches):")
        for r in rows:
            vals = ' | '.join(str(v)[:40] for v in r.values())
            print(f"    → {vals}")
        print()
    
    return results

# ═══════════════════════════════════════════
# Feature 3: Logging System
# ═══════════════════════════════════════════

def log_event(level, message):
    """Log an event to file"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{level}] {message}"
    
    with open(LOG_PATH, 'a') as f:
        f.write(entry + '\n')
    
    print(entry)

def show_logs(lines=20):
    """Show recent log entries"""
    if not os.path.exists(LOG_PATH):
        print("📝 No logs yet")
        return
    
    with open(LOG_PATH, 'r') as f:
        log_lines = f.readlines()
    
    print(f"📝 Recent logs (last {min(lines, len(log_lines))}):\n")
    for line in log_lines[-lines:]:
        print(f"  {line.strip()}")

def clear_logs():
    """Clear log file"""
    if os.path.exists(LOG_PATH):
        open(LOG_PATH, 'w').close()
        print("✅ Logs cleared")

# ═══════════════════════════════════════════
# Feature 4: Task Reminders
# ═══════════════════════════════════════════

def show_task_reminders():
    """Show pending tasks with priority"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT * FROM tasks WHERE done=0 ORDER BY priority DESC")
    tasks = c.fetchall()
    conn.close()
    
    if not tasks:
        print("✅ No pending tasks!")
        return
    
    print("⏰ Task Reminders:\n")
    for t in tasks:
        priority_bar = "🔴" * t['priority'] + "⚪" * (5 - t['priority'])
        print(f"  #{t['id']} {priority_bar} {t['title']}")
        print(f"      Created: {t['created_at']}")
        print()

# ═══════════════════════════════════════════
# Feature 5: Data Visualization (ASCII)
# ═══════════════════════════════════════════

def show_charts():
    """Show ASCII charts of database data"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print("\n" + "="*50)
    print("  📊 DATA VISUALIZATION")
    print("="*50)
    
    # Table sizes
    print("\n📏 Table Sizes:")
    max_count = 0
    sizes = {}
    for t in ['users', 'notes', 'projects', 'tasks']:
        c.execute(f"SELECT COUNT(*) FROM {t}")
        count = c.fetchone()[0]
        sizes[t] = count
        max_count = max(max_count, count)
    
    for t, count in sizes.items():
        bar_len = int((count / max(max_count, 1)) * 30)
        bar = "█" * bar_len
        print(f"  {t:<12} │{bar} {count}")
    
    # Task status
    print("\n✅ Task Status:")
    c.execute("SELECT COUNT(*) FROM tasks WHERE done=1")
    done = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tasks WHERE done=0")
    pending = c.fetchone()[0]
    total = done + pending
    
    if total > 0:
        done_pct = int((done / total) * 30)
        pend_pct = 30 - done_pct
        print(f"  Done    │{'█' * done_pct}{' ' * (30 - done_pct)}│ {done} ({int(done/total*100)}%)")
        print(f"  Pending │{' ' * (30 - pend_pct)}{'█' * pend_pct}│ {pending} ({int(pending/total*100)}%)")
    
    # Priority distribution
    print("\n🎯 Task Priority Distribution:")
    for p in range(6):
        c.execute("SELECT COUNT(*) FROM tasks WHERE priority=?", (p,))
        count = c.fetchone()[0]
        if count > 0:
            bar = "▓" * count * 3
            print(f"  P{p} │{bar} {count}")
    
    conn.close()

# ═══════════════════════════════════════════
# Main Menu
# ═══════════════════════════════════════════

def main():
    log_event("INFO", "Features module started")
    
    print("\n" + "="*50)
    print("  🆕 NEW FEATURES")
    print("="*50)
    print("""
  1. CSV Export/Import
  2. Global Search
  3. Logging System
  4. Task Reminders
  5. Data Visualization (Charts)
""")
    
    # Run all features
    print("Running all features...\n")
    
    # 1. CSV Export
    print("📄 Feature 1: CSV Export")
    export_all_csv()
    
    # 2. Global Search
    print("\n🔍 Feature 2: Global Search")
    global_search("qwen")
    global_search("API")
    
    # 3. Logging
    print("\n📝 Feature 3: Logging")
    log_event("INFO", "System health check passed")
    log_event("WARN", "Database size growing")
    show_logs(5)
    
    # 4. Task Reminders
    print("\n⏰ Feature 4: Task Reminders")
    show_task_reminders()
    
    # 5. Charts
    print("\n📊 Feature 5: Data Visualization")
    show_charts()
    
    print("\n✅ All features demonstrated!")

if __name__ == "__main__":
    main()

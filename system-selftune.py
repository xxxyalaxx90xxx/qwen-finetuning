#!/usr/bin/env python3
"""
System Self-Tuning Module
Automatically adjusts system settings based on usage patterns
"""

import os
import sqlite3
import json
import datetime

DB_PATH = os.path.expanduser("~/my-database.db")
TUNING_PATH = os.path.expanduser("~/tuning-history.json")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def analyze_usage():
    """Analyze how the system is being used"""
    conn = get_db()
    c = conn.cursor()
    
    usage = {
        "timestamp": datetime.datetime.now().isoformat(),
        "tables": {},
        "recommendations": [],
        "tuning_applied": []
    }
    
    for table in ['users', 'notes', 'projects', 'tasks']:
        c.execute(f"SELECT COUNT(*) FROM {table}")
        count = c.fetchone()[0]
        
        if table == 'tasks':
            c.execute("SELECT COUNT(*) FROM tasks WHERE done=0")
            pending = c.fetchone()[0]
            c.execute("SELECT AVG(priority) FROM tasks WHERE done=0")
            avg_pri = c.fetchone()[0] or 0
            usage['tables'][table] = {
                "total": count, "pending": pending, "avg_priority": round(avg_pri, 1)
            }
        else:
            usage['tables'][table] = {"count": count}
    
    usage['db_size_kb'] = os.path.getsize(DB_PATH) // 1024
    
    conn.close()
    return usage

def auto_tune(usage):
    """Apply automatic tuning based on usage"""
    tuning = []
    
    # Adjust based on task load
    tasks = usage['tables'].get('tasks', {})
    if tasks.get('pending', 0) > 10:
        tuning.append("High task load - consider increasing priority thresholds")
    
    # Adjust based on DB size
    if usage['db_size_kb'] > 512:
        tuning.append("Large database - enable aggressive caching")
    elif usage['db_size_kb'] < 50:
        tuning.append("Small database - minimal caching needed")
    
    # Adjust based on notes
    notes = usage['tables'].get('notes', {})
    if notes.get('count', 0) > 50:
        tuning.append("Many notes - consider adding search indexes")
    
    if not tuning:
        tuning.append("System is optimally configured")
    
    usage['recommendations'] = tuning
    return usage

def save_tuning_history(usage):
    """Save tuning history for trend analysis"""
    history = []
    if os.path.exists(TUNING_PATH):
        with open(TUNING_PATH, 'r') as f:
            history = json.load(f)
    
    history.append(usage)
    history = history[-20:]  # Keep last 20 entries
    
    with open(TUNING_PATH, 'w') as f:
        json.dump(history, f, indent=2)

def show_tuning_report():
    """Show current tuning recommendations"""
    print("\n" + "="*50)
    print("  ⚡ SYSTEM SELF-TUNING")
    print("="*50)
    
    usage = analyze_usage()
    usage = auto_tune(usage)
    
    print(f"\n📊 Current State:")
    for table, data in usage['tables'].items():
        if isinstance(data, dict):
            if 'pending' in data:
                print(f"  {table}: {data['total']} total, {data['pending']} pending, avg priority {data['avg_priority']}")
            else:
                print(f"  {table}: {data.get('count', 0)} entries")
    
    print(f"  DB Size: {usage['db_size_kb']} KB")
    
    print(f"\n🔧 Recommendations:")
    for rec in usage['recommendations']:
        print(f"  → {rec}")
    
    save_tuning_history(usage)
    
    print(f"\n✅ Tuning history saved to: {TUNING_PATH}")

def show_history():
    """Show tuning history trends"""
    if not os.path.exists(TUNING_PATH):
        print("📝 No tuning history yet")
        return
    
    with open(TUNING_PATH, 'r') as f:
        history = json.load(f)
    
    print(f"\n📈 Tuning History ({len(history)} entries)\n")
    print(f"  {'Time':<20} {'DB Size':<10} {'Tasks':<10} {'Notes':<10}")
    print("  " + "-"*50)
    for entry in history[-10:]:
        ts = entry['timestamp'][:16]
        size = f"{entry['db_size_kb']}KB"
        tasks = entry['tables'].get('tasks', {}).get('total', 0)
        notes = entry['tables'].get('notes', {}).get('count', 0)
        print(f"  {ts:<20} {size:<10} {tasks:<10} {notes:<10}")

if __name__ == "__main__":
    show_tuning_report()
    show_history()

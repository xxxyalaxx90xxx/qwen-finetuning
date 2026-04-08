#!/usr/bin/env python3
"""
Notification & Reminder System
- Task reminders
- System alerts
- Scheduled notifications
"""

import sqlite3
import os
import datetime
import json

DB_PATH = os.path.expanduser("~/my-database.db")
ALERTS_PATH = os.path.expanduser("~/alerts.json")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def check_task_reminders():
    """Check and display task reminders"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT * FROM tasks WHERE done=0 ORDER BY priority DESC")
    tasks = c.fetchall()
    
    if not tasks:
        print("✅ All tasks completed!")
        conn.close()
        return []
    
    alerts = []
    print("\n⏰ TASK REMINDERS\n" + "="*40)
    
    for t in tasks:
        priority_emoji = "🔴" * t['priority'] + "⚪" * (5 - t['priority'])
        age = datetime.datetime.now() - datetime.datetime.strptime(t['created_at'], "%Y-%m-%d %H:%M:%S")
        
        alert = {
            "type": "TASK",
            "message": f"Task #{t['id']}: {t['title']}",
            "priority": t['priority'],
            "age_days": age.days,
            "timestamp": datetime.datetime.now().isoformat()
        }
        alerts.append(alert)
        
        print(f"\n  {priority_emoji} #{t['id']} {t['title']}")
        print(f"     Created: {t['created_at']} ({age.days}d ago)")
        print(f"     Status:  {'✅ Done' if t['done'] else '⬜ Pending'}")
    
    conn.close()
    return alerts

def check_db_health():
    """Check database health"""
    alerts = []
    
    size = os.path.getsize(DB_PATH)
    if size > 10 * 1024 * 1024:  # 10MB
        alerts.append({
            "type": "WARNING",
            "message": f"Database size: {size//1024}KB",
            "timestamp": datetime.datetime.now().isoformat()
        })
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check for orphaned records
    c.execute("SELECT COUNT(*) FROM tasks WHERE project_id NOT IN (SELECT id FROM projects)")
    orphaned = c.fetchone()[0]
    if orphaned > 0:
        alerts.append({
            "type": "ERROR",
            "message": f"{orphaned} orphaned tasks found",
            "timestamp": datetime.datetime.now().isoformat()
        })
    
    conn.close()
    return alerts

def send_alert(alert_type, message):
    """Send and store an alert"""
    alert = {
        "type": alert_type,
        "message": message,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    # Save to file
    alerts = []
    if os.path.exists(ALERTS_PATH):
        with open(ALERTS_PATH, 'r') as f:
            alerts = json.load(f)
    
    alerts.append(alert)
    
    # Keep last 50
    alerts = alerts[-50:]
    
    with open(ALERTS_PATH, 'w') as f:
        json.dump(alerts, f, indent=2)
    
    # Display
    emoji = {"INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "❌", "TASK": "⏰"}
    print(f"\n  {emoji.get(alert_type, '📢')} [{alert_type}] {message}")

def show_alerts():
    """Show stored alerts"""
    if not os.path.exists(ALERTS_PATH):
        print("📢 No alerts")
        return
    
    with open(ALERTS_PATH, 'r') as f:
        alerts = json.load(f)
    
    print(f"\n📢 Alerts ({len(alerts)} total)\n" + "="*40)
    for a in alerts[-10:]:
        print(f"  [{a['timestamp'][:16]}] {a['type']}: {a['message']}")

def clear_alerts():
    """Clear all alerts"""
    if os.path.exists(ALERTS_PATH):
        open(ALERTS_PATH, 'w').close()
        print("✅ Alerts cleared")

def maintenance():
    """Run maintenance checks"""
    print("\n🔧 System Maintenance\n" + "="*40)
    
    # 1. Task reminders
    task_alerts = check_task_reminders()
    
    # 2. DB health
    health_alerts = check_db_health()
    
    # 3. Send summary
    if task_alerts:
        send_alert("INFO", f"{len(task_alerts)} pending tasks")
    
    if health_alerts:
        for a in health_alerts:
            send_alert(a['type'], a['message'])
    
    # 4. Show recent alerts
    show_alerts()
    
    print("\n✅ Maintenance complete!")

if __name__ == "__main__":
    maintenance()

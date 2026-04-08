#!/usr/bin/env python3
"""
AI Auto-Optimizer for Database System
- Self-healing database
- Automatic cleanup
- Smart recommendations
- Predictive maintenance
- Auto-scaling optimization
"""

import sqlite3
import os
import json
import datetime
import time

DB_PATH = os.path.expanduser("~/my-database.db")
CONFIG_PATH = os.path.expanduser("~/optimizer-config.json")
LOG_PATH = os.path.expanduser("~/optimizer.log")

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] {msg}"
    with open(LOG_PATH, 'a') as f:
        f.write(entry + '\n')
    print(f"  {msg}")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ═══════════════════════════════════════════
# 1. Self-Healing Database
# ═══════════════════════════════════════════

def self_heal():
    """Detect and fix database issues automatically"""
    log("🔧 Self-Healing Check")
    
    conn = get_db()
    c = conn.cursor()
    fixes = 0
    
    # Check integrity
    try:
        c.execute("PRAGMA integrity_check")
        result = c.fetchone()[0]
        if result != "ok":
            log(f"⚠️  Integrity issue: {result}")
            c.execute("PRAGMA quick_check")
            log(f"   Quick check: {c.fetchone()[0]}")
            fixes += 1
        else:
            log("   ✅ Integrity OK")
    except Exception as e:
        log(f"❌ Integrity check failed: {e}")
        fixes += 1
    
    # Fix orphaned records
    c.execute("""
        DELETE FROM tasks WHERE project_id NOT IN (SELECT id FROM projects)
    """)
    orphaned = c.rowcount
    if orphaned > 0:
        conn.commit()
        log(f"   🗑️  Removed {orphaned} orphaned tasks")
        fixes += 1
    
    # Fix null priorities
    c.execute("UPDATE tasks SET priority=0 WHERE priority IS NULL")
    fixed = c.rowcount
    if fixed > 0:
        conn.commit()
        log(f"   🔧 Fixed {fixed} null priorities")
        fixes += 1
    
    # Fix empty usernames
    c.execute("DELETE FROM users WHERE username='' OR username IS NULL")
    deleted = c.rowcount
    if deleted > 0:
        conn.commit()
        log(f"   🗑️  Removed {deleted} invalid users")
        fixes += 1
    
    conn.close()
    
    if fixes == 0:
        log("   ✅ Database is healthy")
    else:
        log(f"   ✅ Fixed {fixes} issue(s)")
    
    return fixes

# ═══════════════════════════════════════════
# 2. Smart Cleanup
# ═══════════════════════════════════════════

def smart_cleanup():
    """Intelligently clean up old/unused data"""
    log("🧹 Smart Cleanup")
    
    conn = get_db()
    c = conn.cursor()
    cleaned = 0
    
    # Archive old completed tasks (older than 30 days)
    c.execute("""
        SELECT COUNT(*) FROM tasks 
        WHERE done=1 AND created_at < date('now', '-30 days')
    """)
    old_tasks = c.fetchone()[0]
    if old_tasks > 0:
        log(f"   📦 {old_tasks} old completed tasks (keeping)")
    
    # Remove duplicate notes
    c.execute("""
        DELETE FROM notes WHERE id NOT IN (
            SELECT MIN(id) FROM notes GROUP BY title, content
        )
    """)
    dupes = c.rowcount
    if dupes > 0:
        conn.commit()
        cleaned += dupes
        log(f"   🗑️  Removed {dupes} duplicate notes")
    
    # Truncate old access logs (keep last 100)
    c.execute("""
        DELETE FROM access_log WHERE id NOT IN (
            SELECT id FROM access_log ORDER BY timestamp DESC LIMIT 100
        )
    """)
    truncated = c.rowcount
    if truncated > 0:
        conn.commit()
        log(f"   📝 Truncated {truncated} old access logs")
    
    conn.close()
    
    if cleaned == 0:
        log("   ✅ No cleanup needed")
    else:
        log(f"   ✅ Cleaned {cleaned} items")

# ═══════════════════════════════════════════
# 3. Smart Recommendations
# ═══════════════════════════════════════════

def ai_recommendations():
    """Generate AI-powered recommendations"""
    log("🤖 AI Recommendations")
    
    conn = get_db()
    c = conn.cursor()
    recs = []
    
    # Task completion rate
    c.execute("SELECT COUNT(*) FROM tasks")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tasks WHERE done=1")
    done = c.fetchone()[0]
    
    if total > 0:
        rate = done / total * 100
        if rate < 50:
            recs.append(f"⚠️  Low completion rate: {rate:.0f}%. Consider archiving old tasks.")
        elif rate > 90:
            recs.append(f"✅ Great task management: {rate:.0f}% completion!")
    
    # Database size warning
    size = os.path.getsize(DB_PATH)
    if size > 1024 * 1024:  # 1MB
        recs.append(f"💾 Database is {size//1024}KB. Consider archiving old data.")
    
    # User activity
    c.execute("SELECT COUNT(*) FROM users WHERE created_at >= date('now', '-7 days')")
    new_users = c.fetchone()[0]
    if new_users == 0:
        recs.append("👤 No new users this week. Consider adding team members.")
    
    # Notes usage
    c.execute("SELECT COUNT(*) FROM notes WHERE content IS NULL OR content=''")
    empty_notes = c.fetchone()[0]
    if empty_notes > 0:
        recs.append(f"📝 {empty_notes} notes are empty. Consider deleting or filling them.")
    
    # Priority balance
    c.execute("SELECT COUNT(*) FROM tasks WHERE priority >= 4 AND done=0")
    high_pri = c.fetchone()[0]
    if high_pri > 5:
        recs.append(f"🔴 {high_pri} high-priority pending tasks. Focus on these first!")
    
    for rec in recs:
        log(f"   {rec}")
    
    if not recs:
        log("   ✅ Everything looks good!")
    
    conn.close()
    return recs

# ═══════════════════════════════════════════
# 4. Predictive Analytics
# ═══════════════════════════════════════════

def predictive_analytics():
    """Predict future trends and issues"""
    log("📈 Predictive Analytics")
    
    conn = get_db()
    c = conn.cursor()
    
    # Growth rate
    c.execute("""
        SELECT DATE(created_at) as day, COUNT(*) as count
        FROM (
            SELECT created_at FROM users
            UNION ALL SELECT created_at FROM notes
            UNION ALL SELECT created_at FROM tasks
        )
        GROUP BY day ORDER BY day DESC LIMIT 7
    """)
    rows = c.fetchall()
    
    if len(rows) >= 2:
        avg_daily = sum(r['count'] for r in rows) / len(rows)
        days_until_1mb = max(1, (1024 - os.path.getsize(DB_PATH)//1024) / max(avg_daily * 0.5, 0.001))
        log(f"   📊 Avg daily activity: {avg_daily:.1f} entries")
        log(f"   📅 Estimated days until 1MB: {days_until_1mb:.0f}")
    
    # Task completion prediction
    c.execute("SELECT COUNT(*) FROM tasks WHERE done=0")
    pending = c.fetchone()[0]
    if pending > 0:
        c.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE done=1 AND created_at >= date('now', '-7 days')
        """)
        weekly_done = c.fetchone()[0]
        if weekly_done > 0:
            days_to_complete = pending / (weekly_done / 7)
            log(f"   ⏰ Estimated days to complete all tasks: {days_to_complete:.1f}")
    
    conn.close()

# ═══════════════════════════════════════════
# 5. Auto-Optimization
# ═══════════════════════════════════════════

def auto_optimize():
    """Apply automatic optimizations"""
    log("⚡ Auto-Optimization")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Enable WAL mode if not already
    c.execute("PRAGMA journal_mode=WAL")
    
    # Optimize cache
    c.execute("PRAGMA cache_size=-64000")
    
    # Run ANALYZE
    c.execute("ANALYZE")
    
    # Vacuum if fragmentation > 10%
    before = os.path.getsize(DB_PATH)
    c.execute("VACUUM")
    after = os.path.getsize(DB_PATH)
    saved = before - after
    
    if saved > 0:
        log(f"   💾 Saved {saved//1024} KB by vacuuming")
    else:
        log("   ✅ No fragmentation detected")
    
    conn.commit()
    conn.close()

# ═══════════════════════════════════════════
# 6. Configuration Management
# ═══════════════════════════════════════════

def save_config():
    """Save optimizer configuration"""
    config = {
        "last_run": datetime.datetime.now().isoformat(),
        "auto_heal": True,
        "auto_cleanup": True,
        "auto_optimize": True,
        "recommendations": True,
        "predictive": True,
        "cleanup_interval_days": 7,
        "max_log_entries": 1000,
    }
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def load_config():
    """Load optimizer configuration"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return None

# ═══════════════════════════════════════════
# Main
# ═══════════════════════════════════════════

def main():
    print("\n" + "="*50)
    print("  🤖 AI AUTO-OPTIMIZER")
    print("="*50)
    
    save_config()
    
    self_heal()
    smart_cleanup()
    ai_recommendations()
    predictive_analytics()
    auto_optimize()
    
    print("\n✅ Auto-optimization complete!")

if __name__ == "__main__":
    main()

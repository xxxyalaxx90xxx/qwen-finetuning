#!/usr/bin/env python3
"""
AI Task Manager - Smart Scheduling & Auto-Prioritization
Uses AI logic to automatically manage tasks
"""

import sqlite3
import os
import datetime
import json

DB_PATH = os.path.expanduser("~/my-database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ═══════════════════════════════════════════
# Smart Task Creation
# ═══════════════════════════════════════════

def smart_add_task(title, project_id=1, description="", deadline="", tags=""):
    """AI-powered task creation with auto-prioritization"""
    
    # Auto-prioritize based on keywords
    priority = 0
    keywords_high = ["urgent", "critical", "wichtig", "sofort", "emergency", "bug"]
    keywords_medium = ["important", "feature", "neu", "todo", "task"]
    keywords_low = ["nice", "maybe", "später", "later", "optional", "idea"]
    
    title_lower = title.lower()
    desc_lower = (description or "").lower()
    full_text = title_lower + " " + desc_lower
    
    if any(kw in full_text for kw in keywords_high):
        priority = 5
    elif any(kw in full_text for kw in keywords_medium):
        priority = 3
    elif any(kw in full_text for kw in keywords_low):
        priority = 1
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""
        INSERT INTO tasks (project_id, title, priority) 
        VALUES (?, ?, ?)
    """, (project_id, title, priority))
    
    task_id = c.lastrowid
    conn.commit()
    conn.close()
    
    priority_label = "🔴 CRITICAL" if priority >= 4 else "🟡 MEDIUM" if priority >= 2 else "⚪ LOW"
    print(f"✅ Task created: #{task_id}")
    print(f"   Title:    {title}")
    print(f"   Priority: {priority_label} ({priority}/5)")
    print(f"   Auto-set based on keywords: {full_text[:50]}")
    
    return task_id

# ═══════════════════════════════════════════
# Smart Prioritization
# ═══════════════════════════════════════════

def ai_reprioritize():
    """AI re-prioritizes all pending tasks based on rules"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT id, title, priority FROM tasks WHERE done=0")
    tasks = c.fetchall()
    
    print("🤖 AI Re-prioritization\n" + "-"*40)
    
    updated = 0
    for task in tasks:
        old_priority = task['priority']
        title = task['title'].lower()
        new_priority = old_priority
        
        # Age-based boost: older tasks get slight priority increase
        c.execute("SELECT created_at FROM tasks WHERE id=?", (task['id'],))
        created = c.fetchone()[0]
        try:
            age = datetime.datetime.now() - datetime.datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
            if age.days > 7:
                new_priority = min(5, old_priority + 1)
        except:
            pass
        
        # Keyword-based adjustments
        if any(kw in title for kw in ["urgent", "critical", "bug", "fix"]):
            new_priority = max(new_priority, 4)
        elif any(kw in title for kw in ["nice", "maybe", "later"]):
            new_priority = min(new_priority, 2)
        
        if new_priority != old_priority:
            c.execute("UPDATE tasks SET priority=? WHERE id=?", (new_priority, task['id']))
            updated += 1
            print(f"   #{task['id']} {task['title'][:30]}: {old_priority} → {new_priority}")
    
    if updated > 0:
        conn.commit()
        print(f"\n✅ Reprioritized {updated} tasks")
    else:
        print("   ✅ All priorities optimal")
    
    conn.close()

# ═══════════════════════════════════════════
# Smart Scheduling
# ═══════════════════════════════════════════

def suggest_daily_plan():
    """Suggest what to work on today"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""
        SELECT id, title, priority, created_at 
        FROM tasks WHERE done=0 
        ORDER BY priority DESC, created_at ASC 
        LIMIT 5
    """)
    tasks = c.fetchall()
    conn.close()
    
    if not tasks:
        print("✅ All tasks done! Take a break 🎉")
        return
    
    print("📅 Today's Plan\n" + "-"*40)
    
    for i, t in enumerate(tasks, 1):
        priority_bar = "🔴" * t['priority'] + "⚪" * (5 - t['priority'])
        print(f"\n  {i}. {t['title']}")
        print(f"     {priority_bar}")
        print(f"     Tip: Start with high-priority items first")
    
    print(f"\n💡 Focus on the top {min(3, len(tasks))} tasks today")

# ═══════════════════════════════════════════
# Task Completion Analysis
# ═══════════════════════════════════════════

def analyze_completion():
    """Analyze task completion patterns"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM tasks")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tasks WHERE done=1")
    done = c.fetchone()[0]
    pending = total - done
    
    print("📊 Task Completion Analysis\n" + "-"*40)
    print(f"  Total:    {total}")
    print(f"  Done:     {done}")
    print(f"  Pending:  {pending}")
    
    if total > 0:
        rate = done / total * 100
        print(f"  Rate:     {rate:.0f}%")
        
        if rate >= 80:
            print(f"  Rating:   🌟 Excellent!")
        elif rate >= 60:
            print(f"  Rating:   👍 Good")
        elif rate >= 40:
            print(f"  Rating:   📊 Average")
        else:
            print(f"  Rating:   ⚠️  Needs attention")
    
    conn.close()

# ═══════════════════════════════════════════
# Main
# ═══════════════════════════════════════════

def main():
    print("\n" + "="*50)
    print("  🤖 AI TASK MANAGER")
    print("="*50)
    
    # Demo: Smart add tasks
    print("\n📝 Smart Task Creation")
    print("-"*40)
    smart_add_task("Fix critical login bug", 1, "Users can't login - urgent")
    smart_add_task("Add new feature later", 1, "Nice to have, not urgent")
    smart_add_task("Important database update", 1, "Important for performance")
    smart_add_task("Maybe add dark mode", 1, "Optional feature")
    
    print("\n")
    ai_reprioritize()
    print("\n")
    suggest_daily_plan()
    print("\n")
    analyze_completion()

if __name__ == "__main__":
    main()

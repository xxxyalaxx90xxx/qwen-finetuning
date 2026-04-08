#!/usr/bin/env python3
"""
Complete Database Toolkit for Termux/Android
SQLite-based - no external dependencies needed
"""

import sqlite3
import os
import json
import sys

DB_PATH = os.path.expanduser("~/my-database.db")

def get_conn(db_path=DB_PATH):
    return sqlite3.connect(db_path)

# ─── Tables ──────────────────────────────────────────────

def create_tables():
    """Create all database tables"""
    conn = get_conn()
    c = conn.cursor()
    
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            content TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            title TEXT NOT NULL,
            done BOOLEAN DEFAULT 0,
            priority INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        );
    """)
    
    conn.commit()
    conn.close()
    print("✅ Tables created: users, notes, projects, tasks")

# ─── Users ───────────────────────────────────────────────

def add_user(username, email=None):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, email) VALUES (?, ?)", (username, email))
        conn.commit()
        print(f"✅ User '{username}' added (ID: {c.lastrowid})")
    except sqlite3.IntegrityError:
        print(f"❌ User '{username}' already exists")
    conn.close()

def list_users():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users ORDER BY id")
    rows = c.fetchall()
    if not rows:
        print("No users found.")
    else:
        print(f"\n{'ID':<5} {'Username':<20} {'Email':<30} {'Created':<20}")
        print("-" * 75)
        for r in rows:
            print(f"{r[0]:<5} {r[1]:<20} {r[2] or '':<30} {r[3]:<20}")
    conn.close()

# ─── Notes ───────────────────────────────────────────────

def add_note(title, content, tags=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO notes (title, content, tags) VALUES (?, ?, ?)", (title, content, tags))
    conn.commit()
    print(f"✅ Note '{title}' added (ID: {c.lastrowid})")
    conn.close()

def search_notes(query):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?",
              (f'%{query}%', f'%{query}%', f'%{query}%'))
    rows = c.fetchall()
    if not rows:
        print(f"No notes matching '{query}'")
    else:
        for r in rows:
            print(f"\n#{r[0]} [{r[4]}] {r[2]}\n{r[3][:200]}")
    conn.close()

def list_notes():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, title, tags, created_at FROM notes ORDER BY id DESC")
    rows = c.fetchall()
    if not rows:
        print("No notes.")
    else:
        print(f"\n{'ID':<5} {'Title':<30} {'Tags':<20} {'Created':<20}")
        print("-" * 75)
        for r in rows:
            print(f"{r[0]:<5} {r[1]:<30} {r[2] or '':<20} {r[3]:<20}")
    conn.close()

# ─── Projects ────────────────────────────────────────────

def add_project(name, desc=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO projects (name, description) VALUES (?, ?)", (name, desc))
    conn.commit()
    print(f"✅ Project '{name}' created (ID: {c.lastrowid})")
    conn.close()

def list_projects():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM projects ORDER BY id")
    rows = c.fetchall()
    if not rows:
        print("No projects.")
    else:
        print(f"\n{'ID':<5} {'Name':<25} {'Status':<10} {'Created':<20}")
        print("-" * 60)
        for r in rows:
            print(f"{r[0]:<5} {r[1]:<25} {r[3]:<10} {r[4]:<20}")
    conn.close()

# ─── Tasks ───────────────────────────────────────────────

def add_task(project_id, title, priority=0):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO tasks (project_id, title, priority) VALUES (?, ?, ?)",
              (project_id, title, priority))
    conn.commit()
    print(f"✅ Task '{title}' added (ID: {c.lastrowid})")
    conn.close()

def list_tasks(project_id=None):
    conn = get_conn()
    c = conn.cursor()
    if project_id:
        c.execute("SELECT * FROM tasks WHERE project_id=? ORDER BY priority DESC, id", (project_id,))
    else:
        c.execute("SELECT * FROM tasks ORDER BY priority DESC, id")
    rows = c.fetchall()
    if not rows:
        print("No tasks.")
    else:
        print(f"\n{'ID':<5} {'Title':<30} {'Done':<6} {'Priority':<10}")
        print("-" * 51)
        for r in rows:
            print(f"{r[0]:<5} {r[3]:<30} {'✅' if r[4] else '⬜':<6} {r[5]:<10}")
    conn.close()

def complete_task(task_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE tasks SET done=1 WHERE id=?", (task_id,))
    conn.commit()
    print(f"✅ Task #{task_id} marked complete")
    conn.close()

# ─── Export/Import ───────────────────────────────────────

def export_json():
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    data = {}
    for table in ["users", "notes", "projects", "tasks"]:
        c.execute(f"SELECT * FROM {table}")
        data[table] = [dict(r) for r in c.fetchall()]
    
    filename = os.path.expanduser("~/database-export.json")
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"✅ Exported to {filename}")
    conn.close()

def db_stats():
    conn = get_conn()
    c = conn.cursor()
    print("\n📊 Database Statistics\n" + "="*30)
    for table in ["users", "notes", "projects", "tasks"]:
        c.execute(f"SELECT COUNT(*) FROM {table}")
        count = c.fetchone()[0]
        print(f"  {table:<12}: {count} rows")
    db_size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
    print(f"  {'Size':<12}: {db_size / 1024:.1f} KB")
    conn.close()

# ─── Interactive CLI ─────────────────────────────────────

def main():
    create_tables()
    
    print("\n" + "="*50)
    print("  Database Toolkit (SQLite3)")
    print(f"  DB: {DB_PATH}")
    print("="*50)
    print("""
  Users:     add-user, list-users
  Notes:     add-note, list-notes, search-notes
  Projects:  add-project, list-projects
  Tasks:     add-task, list-tasks, complete-task
  Other:     stats, export, quit
""")

    while True:
        try:
            cmd = input("db> ").strip().split()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        
        if not cmd:
            continue
        
        action = cmd[0].lower()
        
        if action == "quit":
            break
        elif action == "stats":
            db_stats()
        elif action == "export":
            export_json()
        elif action == "add-user" and len(cmd) >= 2:
            add_user(cmd[1], cmd[2] if len(cmd) > 2 else None)
        elif action == "list-users":
            list_users()
        elif action == "add-note" and len(cmd) >= 3:
            add_note(cmd[1], " ".join(cmd[2:]))
        elif action == "list-notes":
            list_notes()
        elif action == "search-notes" and len(cmd) >= 2:
            search_notes(" ".join(cmd[1:]))
        elif action == "add-project" and len(cmd) >= 2:
            add_project(cmd[1], " ".join(cmd[2:]) if len(cmd) > 2 else "")
        elif action == "list-projects":
            list_projects()
        elif action == "add-task" and len(cmd) >= 3:
            add_task(int(cmd[1]), " ".join(cmd[2:]))
        elif action == "list-tasks":
            list_tasks(int(cmd[1]) if len(cmd) > 1 else None)
        elif action == "complete-task" and len(cmd) >= 2:
            complete_task(int(cmd[1]))
        else:
            print(f"Unknown command: {action}")

if __name__ == "__main__":
    main()

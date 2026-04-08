#!/usr/bin/env python3
"""
Qwen AI Database Assistant
Uses natural language to query and manage your database
Zero external API needed - uses local SQLite + simple AI logic
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

def ai_process(query):
    """Simple AI query processor - mimics LLM understanding"""
    q = query.lower()
    conn = get_db()
    c = conn.cursor()
    result = ""

    # Count queries
    if any(w in q for w in ["how many", "count", "wie viele", "anzahl"]):
        if "user" in q:
            c.execute("SELECT COUNT(*) FROM users")
            result = f"📊 You have {c.fetchone()[0]} users"
        elif "note" in q:
            c.execute("SELECT COUNT(*) FROM notes")
            result = f"📊 You have {c.fetchone()[0]} notes"
        elif "project" in q:
            c.execute("SELECT COUNT(*) FROM projects")
            result = f"📊 You have {c.fetchone()[0]} projects"
        elif "task" in q:
            c.execute("SELECT COUNT(*) FROM tasks")
            c.execute("SELECT COUNT(*) FROM tasks WHERE done=1")
            done = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM tasks WHERE done=0")
            pending = c.fetchone()[0]
            result = f"📊 Tasks: {done} done, {pending} pending"

    # List queries
    elif any(w in q for w in ["show", "list", "display", "zeigen", "liste"]):
        if "user" in q:
            c.execute("SELECT * FROM users")
            rows = c.fetchall()
            result = "👤 Users:\n" + "\n".join(f"  - {r['username']} ({r['email'] or 'no email'})" for r in rows)
        elif "note" in q:
            c.execute("SELECT id, title FROM notes ORDER BY id DESC")
            rows = c.fetchall()
            result = "📝 Notes:\n" + "\n".join(f"  #{r['id']} {r['title']}" for r in rows)
        elif "project" in q:
            c.execute("SELECT * FROM projects")
            rows = c.fetchall()
            result = "📁 Projects:\n" + "\n".join(f"  - {r['name']} [{r['status']}]" for r in rows)
        elif "task" in q:
            c.execute("SELECT id, title, done, priority FROM tasks ORDER BY priority DESC")
            rows = c.fetchall()
            result = "✅ Tasks:\n" + "\n".join(f"  {'✅' if r['done'] else '⬜'} #{r['id']} {r['title']} (P{r['priority']})" for r in rows)
        elif "all" in q or "everything" in q or "alles" in q:
            stats = {}
            for t in ['users','notes','projects','tasks']:
                c.execute(f"SELECT COUNT(*) FROM {t}")
                stats[t] = c.fetchone()[0]
            result = f"📊 Database Summary:\n"
            for k,v in stats.items():
                result += f"  {k}: {v}\n"

    # Search queries
    elif any(w in q for w in ["search", "find", "suchen", "finden", "look for"]):
        keyword = query.split()[-1] if query.split() else ""
        if keyword:
            c.execute("SELECT title, content FROM notes WHERE title LIKE ? OR content LIKE ?",
                     (f'%{keyword}%', f'%{keyword}%'))
            rows = c.fetchall()
            if rows:
                result = f"🔍 Found {len(rows)} note(s):\n" + "\n".join(f"  - {r['title']}: {r['content'][:50]}" for r in rows)
            else:
                result = f"🔍 No notes found for '{keyword}'"

    # Add queries
    elif any(w in q for w in ["add", "create", "new", "erstellen", "hinzufügen"]):
        if "user" in q:
            parts = query.split()
            if len(parts) >= 4:
                name, email = parts[-2], parts[-1]
            else:
                name = input("Username: ")
                email = input("Email: ")
            c.execute("INSERT INTO users (username, email) VALUES (?, ?)", (name, email))
            conn.commit()
            result = f"✅ User '{name}' created"
        elif "note" in q:
            # Try to parse: "add note title here is the content"
            note_parts = query.lower().split("note", 1)[-1].strip().split()
            if len(note_parts) >= 2:
                title = note_parts[0]
                content = " ".join(note_parts[1:])
            else:
                title = input("Note title: ")
                content = input("Note content: ")
            c.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
            conn.commit()
            result = f"✅ Note '{title}' created"
        elif "project" in q:
            proj_parts = query.lower().split("project", 1)[-1].strip().split(None, 1)
            if proj_parts:
                name = proj_parts[0]
                desc = proj_parts[1] if len(proj_parts) > 1 else ""
            else:
                name = input("Project name: ")
                desc = input("Description: ")
            c.execute("INSERT INTO projects (name, description) VALUES (?, ?)", (name, desc))
            conn.commit()
            result = f"✅ Project '{name}' created"
        elif "task" in q:
            task_parts = query.lower().split("task", 1)[-1].strip().split(None, 1)
            if task_parts:
                title = task_parts[0] if len(task_parts) >= 1 else "new task"
                pid = "1"
                if len(task_parts) >= 2:
                    content = task_parts[1]
            else:
                title = input("Task title: ")
                pid = input("Project ID (1): ") or "1"
            c.execute("INSERT INTO tasks (project_id, title, priority) VALUES (?, ?, ?)",
                     (int(pid), title, 0))
            conn.commit()
            result = f"✅ Task '{title}' created"

    # Complete queries
    elif any(w in q for w in ["complete", "done", "finish", "erledigt", "fertig"]):
        parts = query.split()
        for p in parts:
            if p.isdigit():
                c.execute("UPDATE tasks SET done=1 WHERE id=?", (int(p),))
                conn.commit()
                result = f"✅ Task #{p} marked complete"
                break
        if not result:
            result = "Please specify task ID, e.g., 'complete task 1'"

    # Delete queries
    elif any(w in q for w in ["delete", "remove", "löschen", "entfernen"]):
        parts = query.split()
        for p in parts:
            if p.isdigit():
                table = "tasks" if "task" in q else "notes" if "note" in q else "users" if "user" in q else "projects"
                c.execute(f"DELETE FROM {table} WHERE id=?", (int(p),))
                conn.commit()
                result = f"🗑️ {table[:-1]} #{p} deleted"
                break
        if not result:
            result = "Please specify what to delete and ID"

    # Stats
    elif any(w in q for w in ["stats", "statistic", "status", "info", "summary"]):
        stats = {}
        for t in ['users','notes','projects','tasks']:
            c.execute(f"SELECT COUNT(*) FROM {t}")
            stats[t] = c.fetchone()[0]
        stats['size'] = os.path.getsize(DB_PATH) // 1024
        result = "📊 Database Stats:\n" + "\n".join(f"  {k}: {v}" for k,v in stats.items())

    # Help
    elif any(w in q for w in ["help", "hilfe", "commands", "was kann"]):
        result = """🤖 AI Database Assistant - Commands:

  "how many users?"        → Count users
  "show all tasks"         → List tasks
  "search notes qwen"      → Search notes
  "add user alice@a.com"   → Create user
  "add note title content" → Create note
  "complete task 1"        → Mark task done
  "delete note 2"          → Delete item
  "stats"                  → Database stats
  "show everything"        → Full summary"""

    else:
        result = "🤔 I didn't understand. Try 'help' for commands."

    conn.close()
    return result

def main():
    print("\n" + "="*50)
    print("  🤖 AI Database Assistant")
    print(f"  DB: {DB_PATH}")
    print("="*50)
    print("  Type 'quit' to exit, 'help' for commands\n")

    while True:
        try:
            query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        
        if query.lower() in ("quit", "exit", "q"):
            break
        if not query:
            continue
        
        print(f"\nAI: {ai_process(query)}\n")

if __name__ == "__main__":
    main()

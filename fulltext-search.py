#!/usr/bin/env python3
"""
Full-Text Search Engine (FTS5)
Advanced search across all database tables
"""

import sqlite3
import os

DB_PATH = os.path.expanduser("~/my-database.db")

def setup_fts():
    """Enable FTS5 virtual tables for full-text search"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create FTS tables
    fts_tables = [
        "CREATE VIRTUAL TABLE IF NOT EXISTS fts_notes USING fts5(title, content, tags)",
        "CREATE VIRTUAL TABLE IF NOT EXISTS fts_tasks USING fts5(title)",
        "CREATE VIRTUAL TABLE IF NOT EXISTS fts_users USING fts5(username, email)",
        "CREATE VIRTUAL TABLE IF NOT EXISTS fts_projects USING fts5(name, description)",
    ]
    
    for sql in fts_tables:
        c.execute(sql)
    
    # Populate FTS tables from existing data
    c.execute("INSERT OR IGNORE INTO fts_notes SELECT title, COALESCE(content,''), COALESCE(tags,'') FROM notes")
    c.execute("INSERT OR IGNORE INTO fts_tasks SELECT title FROM tasks")
    c.execute("INSERT OR IGNORE INTO fts_users SELECT username, COALESCE(email,'') FROM users")
    c.execute("INSERT OR IGNORE INTO fts_projects SELECT name, COALESCE(description,'') FROM projects")
    
    # Create triggers for auto-sync
    triggers = [
        """CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN
           INSERT INTO fts_notes(rowid, title, content, tags) VALUES (new.id, new.title, COALESCE(new.content,''), COALESCE(new.tags,''));
        END""",
        """CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON notes BEGIN
           DELETE FROM fts_notes WHERE rowid = old.id;
        END""",
        """CREATE TRIGGER IF NOT EXISTS tasks_ai AFTER INSERT ON tasks BEGIN
           INSERT INTO fts_tasks(rowid, title) VALUES (new.id, new.title);
        END""",
    ]
    
    for trigger in triggers:
        c.execute(trigger)
    
    conn.commit()
    conn.close()
    print("✅ FTS5 search engine initialized")

def search_fts(query, limit=20):
    """Full-text search across all tables"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    results = {}
    
    # Search notes
    try:
        c.execute("SELECT rowid, title, snippet(content, 0, '[', ']', '...', 50) as preview FROM fts_notes WHERE fts_notes MATCH ? LIMIT ?", (query, limit))
        rows = c.fetchall()
        if rows:
            results['notes'] = [dict(r) for r in rows]
    except:
        pass
    
    # Search tasks
    try:
        c.execute("SELECT rowid, title FROM fts_tasks WHERE fts_tasks MATCH ? LIMIT ?", (query, limit))
        rows = c.fetchall()
        if rows:
            results['tasks'] = [dict(r) for r in rows]
    except:
        pass
    
    # Search users
    try:
        c.execute("SELECT rowid, username, email FROM fts_users WHERE fts_users MATCH ? LIMIT ?", (query, limit))
        rows = c.fetchall()
        if rows:
            results['users'] = [dict(r) for r in rows]
    except:
        pass
    
    # Search projects
    try:
        c.execute("SELECT rowid, name, description FROM fts_projects WHERE fts_projects MATCH ? LIMIT ?", (query, limit))
        rows = c.fetchall()
        if rows:
            results['projects'] = [dict(r) for r in rows]
    except:
        pass
    
    conn.close()
    
    # Display results
    total = sum(len(v) for v in results.values())
    print(f"\n🔍 Search: '{query}' ({total} results)\n")
    print("="*60)
    
    for table, rows in results.items():
        print(f"\n📂 {table.upper()} ({len(rows)} matches):")
        for r in rows:
            vals = ' | '.join(f"{k}: {v}" for k, v in r.items())
            print(f"  → {vals}")
    
    if not results:
        print("  No results found.")
    
    return results

def search_demo():
    """Demonstrate FTS search capabilities"""
    print("\n" + "="*60)
    print("  🔍 FULL-TEXT SEARCH ENGINE")
    print("="*60)
    
    queries = ["qwen", "API", "task", "feature", "bug"]
    
    for q in queries:
        search_fts(q, limit=3)
        print()

if __name__ == "__main__":
    setup_fts()
    search_demo()

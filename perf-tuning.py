#!/usr/bin/env python3
"""
Database Performance Tuning Module
Optimizes SQLite3 for maximum speed on Android/Termux
"""

import sqlite3
import os
import time
import json

DB_PATH = os.path.expanduser("~/my-database.db")

def optimize_db():
    """Apply all SQLite optimizations"""
    print("🔧 Database Performance Tuning\n" + "="*40)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. PRAGMA optimizations
    print("\n1️⃣ Applying PRAGMA optimizations...")
    pragmas = {
        "journal_mode": "WAL",              # Write-Ahead Logging
        "synchronous": "NORMAL",            # Balanced safety/speed
        "cache_size": "-64000",             # 64MB cache
        "foreign_keys": "ON",               # Enforce FK constraints
        "temp_store": "MEMORY",             # Store temp tables in RAM
        "mmap_size": "268435456",           # 256MB memory-mapped I/O
        "optimize": "",                     # Run ANALYZE optimization
    }
    
    for pragma, value in pragmas.items():
        if value:
            c.execute(f"PRAGMA {pragma} = {value}")
        else:
            c.execute(f"PRAGMA {pragma}")
        result = c.fetchone()
        print(f"   {pragma} = {result[0] if result else 'OK'}")
    
    # 2. Create indexes for faster queries
    print("\n2️⃣ Creating performance indexes...")
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_notes_title ON notes(title)",
        "CREATE INDEX IF NOT EXISTS idx_notes_content ON notes(content)",
        "CREATE INDEX IF NOT EXISTS idx_notes_tags ON notes(tags)",
        "CREATE INDEX IF NOT EXISTS idx_tasks_done ON tasks(done)",
        "CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)",
        "CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id)",
        "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
        "CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)",
    ]
    
    for idx in indexes:
        try:
            c.execute(idx)
            name = idx.split("idx_")[1].split(" ")[0]
            print(f"   ✅ Index: {name}")
        except sqlite3.OperationalError as e:
            print(f"   ⚠️  {e}")
    
    # 3. Vacuum database
    print("\n3️⃣ Vacuuming database...")
    before = os.path.getsize(DB_PATH)
    start = time.time()
    c.execute("VACUUM")
    conn.commit()
    after = os.path.getsize(DB_PATH)
    elapsed = time.time() - start
    saved = before - after
    print(f"   Before: {before//1024} KB")
    print(f"   After:  {after//1024} KB")
    print(f"   Saved:  {saved//1024} KB ({elapsed:.2f}s)")
    
    # 4. Analyze tables for query planner
    print("\n4️⃣ Analyzing tables...")
    c.execute("ANALYZE")
    conn.commit()
    print("   ✅ Query optimizer updated")
    
    # 5. Show table stats
    print("\n5️⃣ Table Statistics:")
    tables = ['users', 'notes', 'projects', 'tasks']
    for t in tables:
        c.execute(f"SELECT COUNT(*) FROM {t}")
        count = c.fetchone()[0]
        c.execute(f"PRAGMA index_list({t})")
        indexes = c.fetchall()
        print(f"   {t}: {count} rows, {len(indexes)} indexes")
    
    conn.close()
    print("\n✅ Database optimization complete!")

def benchmark_db():
    """Run performance benchmarks"""
    print("\n📊 Performance Benchmark\n" + "="*40)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Test 1: Simple query
    start = time.time()
    for _ in range(100):
        c.execute("SELECT * FROM users")
    elapsed = time.time() - start
    print(f"   100 SELECT * FROM users:  {elapsed*10:.1f}ms")
    
    # Test 2: Indexed query
    start = time.time()
    for _ in range(100):
        c.execute("SELECT * FROM tasks WHERE priority > 0")
    elapsed = time.time() - start
    print(f"   100 SELECT by priority:   {elapsed*10:.1f}ms")
    
    # Test 3: Insert
    start = time.time()
    for i in range(50):
        c.execute("INSERT INTO notes (title, content) VALUES (?, ?)",
                 (f"bench_{i}", "benchmark test"))
    conn.commit()
    elapsed = time.time() - start
    print(f"   50 INSERTs:               {elapsed*10:.1f}ms")
    
    # Cleanup benchmark data
    c.execute("DELETE FROM notes WHERE title LIKE 'bench_%'")
    conn.commit()
    
    # Test 4: Complex join
    start = time.time()
    c.execute("""
        SELECT t.title, p.name as project 
        FROM tasks t 
        LEFT JOIN projects p ON t.project_id = p.id 
        ORDER BY t.priority DESC
    """)
    results = c.fetchall()
    elapsed = time.time() - start
    print(f"   Complex JOIN query:       {elapsed*1000:.1f}ms")
    
    conn.close()
    print("\n✅ Benchmark complete!")

def show_db_info():
    """Show database configuration info"""
    print("\n📋 Database Info\n" + "="*40)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    info = [
        ("Version", sqlite3.sqlite_version),
        ("Size", f"{os.path.getsize(DB_PATH)//1024} KB"),
        ("File", DB_PATH),
    ]
    
    for key, val in info:
        print(f"   {key:<12}: {val}")
    
    print("\n   PRAGMAs:")
    for pragma in ["journal_mode", "synchronous", "cache_size", "foreign_keys", "temp_store"]:
        c.execute(f"PRAGMA {pragma}")
        result = c.fetchone()
        print(f"   {pragma:<12}: {result[0]}")
    
    print("\n   Indexes:")
    c.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
    for row in c.fetchall():
        print(f"   ✅ {row[0]} ({row[1]})")
    
    conn.close()

if __name__ == "__main__":
    optimize_db()
    benchmark_db()
    show_db_info()

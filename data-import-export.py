#!/usr/bin/env python3
"""
Advanced Data Import/Export Module
Supports: JSON, XML, YAML, CSV, SQL
"""

import sqlite3
import os
import json
import csv
import datetime

DB_PATH = os.path.expanduser("~/my-database.db")
EXPORT_DIR = os.path.expanduser("~/exports")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def export_json():
    """Export database to JSON"""
    os.makedirs(EXPORT_DIR, exist_ok=True)
    conn = get_db()
    c = conn.cursor()
    
    data = {"exported": datetime.datetime.now().isoformat(), "tables": {}}
    for table in ['users', 'notes', 'projects', 'tasks']:
        c.execute(f"SELECT * FROM {table}")
        data["tables"][table] = [dict(r) for r in c.fetchall()]
    conn.close()
    
    path = os.path.join(EXPORT_DIR, "database.json")
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ JSON: {path} ({os.path.getsize(path)//1024}KB)")

def export_xml():
    """Export database to XML"""
    os.makedirs(EXPORT_DIR, exist_ok=True)
    conn = get_db()
    c = conn.cursor()
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<database>\n'
    xml += f'  <exported>{datetime.datetime.now().isoformat()}</exported>\n'
    
    for table in ['users', 'notes', 'projects', 'tasks']:
        xml += f'  <{table}>\n'
        c.execute(f"SELECT * FROM {table}")
        for row in c.fetchall():
            xml += '    <row>\n'
            for key in row.keys():
                val = str(row[key] or '').replace('&', '&amp;').replace('<', '&lt;')
                xml += f'      <{key}>{val}</{key}>\n'
            xml += '    </row>\n'
        xml += f'  </{table}>\n'
    
    xml += '</database>'
    conn.close()
    
    path = os.path.join(EXPORT_DIR, "database.xml")
    with open(path, 'w') as f:
        f.write(xml)
    
    print(f"✅ XML: {path} ({os.path.getsize(path)//1024}KB)")

def export_yaml():
    """Export database to YAML (no external lib needed)"""
    os.makedirs(EXPORT_DIR, exist_ok=True)
    conn = get_db()
    c = conn.cursor()
    
    yaml = f"# Database Export\n# Date: {datetime.datetime.now().isoformat()}\n\n"
    
    for table in ['users', 'notes', 'projects', 'tasks']:
        yaml += f"{table}:\n"
        c.execute(f"SELECT * FROM {table}")
        for row in c.fetchall():
            yaml += f"  - id: {row['id']}\n"
            for key in row.keys():
                if key == 'id':
                    continue
                val = row[key] or ''
                yaml += f"    {key}: \"{val}\"\n"
    
    conn.close()
    
    path = os.path.join(EXPORT_DIR, "database.yaml")
    with open(path, 'w') as f:
        f.write(yaml)
    
    print(f"✅ YAML: {path} ({os.path.getsize(path)//1024}KB)")

def export_csv_all():
    """Export all tables to individual CSV files"""
    os.makedirs(EXPORT_DIR, exist_ok=True)
    conn = get_db()
    c = conn.cursor()
    
    for table in ['users', 'notes', 'projects', 'tasks']:
        c.execute(f"SELECT * FROM {table}")
        rows = c.fetchall()
        if not rows:
            continue
        
        path = os.path.join(EXPORT_DIR, f"{table}.csv")
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(rows[0].keys())
            for row in rows:
                writer.writerow(list(row))
        
        print(f"✅ CSV: {path} ({os.path.getsize(path)//1024}KB)")
    
    conn.close()

def export_sql():
    """Export database as SQL dump"""
    os.makedirs(EXPORT_DIR, exist_ok=True)
    conn = get_db()
    c = conn.cursor()
    
    sql = f"-- Database Dump\n-- Date: {datetime.datetime.now().isoformat()}\n\n"
    
    for table in ['users', 'notes', 'projects', 'tasks']:
        sql += f"-- Table: {table}\n"
        c.execute(f"SELECT * FROM {table}")
        for row in c.fetchall():
            vals = ", ".join(f"'{str(v).replace(chr(39), chr(39)+chr(39))}'" for v in row)
            sql += f"INSERT INTO {table} VALUES ({vals});\n"
        sql += "\n"
    
    conn.close()
    
    path = os.path.join(EXPORT_DIR, "database.sql")
    with open(path, 'w') as f:
        f.write(sql)
    
    print(f"✅ SQL: {path} ({os.path.getsize(path)//1024}KB)")

def import_json(filepath):
    """Import database from JSON"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    imported = 0
    for table, rows in data.get('tables', {}).items():
        for row in rows:
            cols = ', '.join(row.keys())
            placeholders = ', '.join(['?' for _ in row])
            try:
                c.execute(f"INSERT OR IGNORE INTO {table} ({cols}) VALUES ({placeholders})", list(row.values()))
                imported += 1
            except:
                pass
    
    conn.commit()
    conn.close()
    print(f"✅ Imported {imported} rows from {filepath}")

def main():
    print("\n" + "="*50)
    print("  📦 DATA IMPORT/EXPORT")
    print("="*50)
    
    print("\n📤 Exporting...\n")
    export_json()
    export_xml()
    export_yaml()
    export_csv_all()
    export_sql()
    
    print(f"\n✅ All exports saved to: {EXPORT_DIR}")

if __name__ == "__main__":
    main()

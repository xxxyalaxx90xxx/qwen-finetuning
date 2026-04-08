#!/usr/bin/env python3
"""
REST API Server for Database
Zero dependencies, works on Termux/Android
Endpoints:
  GET  /api/users       - List users
  POST /api/users       - Create user
  GET  /api/notes       - List notes
  POST /api/notes       - Create note
  GET  /api/projects    - List projects
  POST /api/projects    - Create project
  GET  /api/tasks       - List tasks
  POST /api/tasks       - Create task
  POST /api/tasks/:id/complete - Complete task
  GET  /api/stats       - Database stats
  GET  /api/export      - Full export
"""

import http.server
import sqlite3
import json
import os
import urllib.parse

DB_PATH = os.path.expanduser("~/my-database.db")
API_PORT = 3000

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class APIHandler(http.server.BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, default=str).encode())
    
    def read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        if length:
            return json.loads(self.rfile.read(length))
        return {}
    
    def do_GET(self):
        path = self.path.rstrip('/')
        
        if path == '/api/stats':
            conn = get_db()
            c = conn.cursor()
            stats = {}
            for t in ['users','notes','projects','tasks']:
                c.execute(f"SELECT COUNT(*) FROM {t}")
                stats[t] = c.fetchone()[0]
            stats['size_kb'] = os.path.getsize(DB_PATH) // 1024
            conn.close()
            self.send_json(stats)
        
        elif path == '/api/export':
            conn = get_db()
            data = {}
            for t in ['users','notes','projects','tasks']:
                c = conn.cursor()
                c.execute(f"SELECT * FROM {t}")
                data[t] = [dict(r) for r in c.fetchall()]
            conn.close()
            self.send_json(data)
        
        elif path in ['/api/users', '/api/notes', '/api/projects', '/api/tasks']:
            table = path.split('/')[-1]
            conn = get_db()
            c = conn.cursor()
            c.execute(f"SELECT * FROM {table} ORDER BY id DESC")
            rows = [dict(r) for r in c.fetchall()]
            conn.close()
            self.send_json({table: rows, "total": len(rows)})
        
        else:
            self.send_json({
                "name": "Database API",
                "version": "1.0",
                "endpoints": {
                    "GET /api/stats": "Database statistics",
                    "GET /api/export": "Full database export",
                    "GET /api/users": "List users",
                    "GET /api/notes": "List notes",
                    "GET /api/projects": "List projects",
                    "GET /api/tasks": "List tasks",
                    "POST /api/users": '{"username":"name","email":"email"}',
                    "POST /api/notes": '{"title":"t","content":"c"}',
                    "POST /api/projects": '{"name":"n","desc":"d"}',
                    "POST /api/tasks": '{"project_id":1,"title":"t","priority":0}',
                    "POST /api/tasks/:id/complete": '{"id":1}'
                }
            })
    
    def do_POST(self):
        path = self.path.rstrip('/')
        body = self.read_body()
        conn = get_db()
        c = conn.cursor()
        
        try:
            if path == '/api/users':
                c.execute("INSERT INTO users (username, email) VALUES (?, ?)",
                         (body.get('username',''), body.get('email','')))
                conn.commit()
                self.send_json({"ok": True, "id": c.lastrowid, "message": "User created"})
            
            elif path == '/api/notes':
                c.execute("INSERT INTO notes (title, content, tags) VALUES (?, ?, ?)",
                         (body.get('title',''), body.get('content',''), body.get('tags','')))
                conn.commit()
                self.send_json({"ok": True, "id": c.lastrowid, "message": "Note created"})
            
            elif path == '/api/projects':
                c.execute("INSERT INTO projects (name, description) VALUES (?, ?)",
                         (body.get('name',''), body.get('desc','')))
                conn.commit()
                self.send_json({"ok": True, "id": c.lastrowid, "message": "Project created"})
            
            elif path == '/api/tasks':
                c.execute("INSERT INTO tasks (project_id, title, priority) VALUES (?, ?, ?)",
                         (int(body.get('project_id',1)), body.get('title',''), int(body.get('priority',0))))
                conn.commit()
                self.send_json({"ok": True, "id": c.lastrowid, "message": "Task created"})
            
            elif path.startswith('/api/tasks/') and path.endswith('/complete'):
                task_id = int(path.split('/')[-2])
                c.execute("UPDATE tasks SET done=1 WHERE id=?", (task_id,))
                conn.commit()
                self.send_json({"ok": True, "message": f"Task {task_id} completed"})
            
            else:
                self.send_json({"error": "Unknown endpoint"}, 404)
        
        except Exception as e:
            conn.rollback()
            self.send_json({"error": str(e)}, 500)
        
        conn.close()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, *args):
        print(f"[API] {args[0]}")

if __name__ == '__main__':
    print(f"\n  Database REST API Server")
    print(f"  http://localhost:{API_PORT}")
    print(f"  http://127.0.0.1:{API_PORT}")
    print(f"  Docs: http://localhost:{API_PORT}/")
    print(f"  Press Ctrl+C to stop\n")
    server = http.server.HTTPServer(('0.0.0.0', API_PORT), APIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

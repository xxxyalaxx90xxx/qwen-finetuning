#!/usr/bin/env python3
"""
Security Module for Database System
- User authentication
- Data encryption
- Access logging
- Session management
"""

import sqlite3
import hashlib
import os
import json
import datetime
import secrets

DB_PATH = os.path.expanduser("~/my-database.db")
SESSIONS = {}

def hash_password(password):
    """Hash password with SHA-256 + salt"""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hashed}"

def verify_password(stored, password):
    """Verify password against stored hash"""
    salt, hashed = stored.split("$")
    return hashlib.sha256((salt + password).encode()).hexdigest() == hashed

def create_auth_table():
    """Create authentication tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS auth_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS auth_sessions (
            id TEXT PRIMARY KEY,
            user_id INTEGER,
            ip TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES auth_users(id)
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS access_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            resource TEXT,
            ip TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES auth_users(id)
        )
    """)
    
    conn.commit()
    conn.close()

def register_user(username, password, role="user"):
    """Register a new user"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        pw_hash = hash_password(password)
        c.execute("INSERT INTO auth_users (username, password_hash, role) VALUES (?, ?, ?)",
                 (username, pw_hash, role))
        conn.commit()
        print(f"✅ User '{username}' registered (role: {role})")
        log_action(c.lastrowid, "REGISTER", f"User created: {username}")
    except sqlite3.IntegrityError:
        print(f"❌ User '{username}' already exists")
    
    conn.close()

def login(username, password):
    """Login and create session"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT * FROM auth_users WHERE username=?", (username,))
    user = c.fetchone()
    
    if not user:
        print(f"❌ User '{username}' not found")
        conn.close()
        return None
    
    if not verify_password(user['password_hash'], password):
        print(f"❌ Wrong password for '{username}'")
        conn.close()
        return None
    
    # Update last login
    c.execute("UPDATE auth_users SET last_login=CURRENT_TIMESTAMP WHERE id=?", (user['id'],))
    
    # Create session
    session_id = secrets.token_urlsafe(32)
    expires = (datetime.datetime.now() + datetime.timedelta(hours=24)).isoformat()
    c.execute("INSERT INTO auth_sessions (id, user_id, expires_at) VALUES (?, ?, ?)",
             (session_id, user['id'], expires))
    conn.commit()
    
    SESSIONS[session_id] = {
        'user_id': user['id'],
        'username': user['username'],
        'role': user['role'],
        'expires': expires
    }
    
    log_action(user['id'], "LOGIN", f"Session created: {session_id[:8]}...")
    conn.close()
    
    print(f"✅ Logged in as '{username}' (role: {user['role']})")
    print(f"   Session: {session_id}")
    return session_id

def check_session(session_id):
    """Check if session is valid"""
    if session_id in SESSIONS:
        session = SESSIONS[session_id]
        if datetime.datetime.fromisoformat(session['expires']) > datetime.datetime.now():
            return session
    return None

def log_action(user_id, action, resource=""):
    """Log an access event"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO access_log (user_id, action, resource) VALUES (?, ?, ?)",
             (user_id, action, resource))
    conn.commit()
    conn.close()

def show_access_log():
    """Show recent access log entries"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("""
        SELECT al.*, au.username 
        FROM access_log al 
        LEFT JOIN auth_users au ON al.user_id = au.id 
        ORDER BY al.timestamp DESC LIMIT 20
    """)
    rows = c.fetchall()
    
    if not rows:
        print("📝 No access logs yet")
        conn.close()
        return
    
    print("📝 Access Log:\n")
    print(f"  {'Time':<20} {'User':<12} {'Action':<12} {'Resource'}")
    print("  " + "-"*70)
    for r in rows:
        print(f"  {r['timestamp']:<20} {r['username'] or 'system':<12} {r['action']:<12} {r['resource'][:30]}")
    
    conn.close()

def encrypt_data(data, key="default"):
    """Simple XOR encryption (for demo - use proper crypto in production)"""
    key_bytes = key.encode() * (len(data) // len(key) + 1)
    encrypted = bytes(a ^ b for a, b in zip(data.encode(), key_bytes))
    return encrypted.hex()

def decrypt_data(hex_data, key="default"):
    """Decrypt XOR encrypted data"""
    data = bytes.fromhex(hex_data)
    key_bytes = key.encode() * (len(data) // len(key) + 1)
    return bytes(a ^ b for a, b in zip(data, key_bytes)).decode()

def main():
    print("\n" + "="*50)
    print("  🔐 Security Module")
    print("="*50)
    
    create_auth_table()
    
    # Register test users
    print("\n📝 Registering users...")
    register_user("admin", "admin123", "admin")
    register_user("user1", "password1", "user")
    
    # Login
    print("\n🔑 Testing login...")
    session = login("admin", "admin123")
    
    # Show logs
    print("\n📋 Access log:")
    show_access_log()
    
    # Test encryption
    print("\n🔒 Testing encryption...")
    secret = "Hello World - This is confidential data"
    encrypted = encrypt_data(secret, "mykey")
    decrypted = decrypt_data(encrypted, "mykey")
    print(f"   Original:  {secret}")
    print(f"   Encrypted: {encrypted[:40]}...")
    print(f"   Decrypted: {decrypted}")
    
    print("\n✅ Security module complete!")

if __name__ == "__main__":
    main()

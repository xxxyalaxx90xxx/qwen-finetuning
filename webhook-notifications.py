#!/usr/bin/env python3
"""
Webhook Notification System
Send alerts to external services via HTTP
"""

import httpx
import sqlite3
import os
import json
import datetime

DB_PATH = os.path.expanduser("~/my-database.db")
WEBHOOK_CONFIG = os.path.expanduser("~/webhooks.json")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def load_webhooks():
    """Load webhook configurations"""
    if os.path.exists(WEBHOOK_CONFIG):
        with open(WEBHOOK_CONFIG, 'r') as f:
            return json.load(f)
    return {
        "discord": None,
        "slack": None,
        "webhook_url": None,
        "email": None
    }

def save_webhooks(config):
    """Save webhook configurations"""
    with open(WEBHOOK_CONFIG, 'w') as f:
        json.dump(config, f, indent=2)

def send_webhook(url, payload, service="generic"):
    """Send webhook notification"""
    try:
        resp = httpx.post(url, json=payload, timeout=10)
        if resp.status_code < 400:
            print(f"  ✅ {service}: Sent successfully")
        else:
            print(f"  ⚠️  {service}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"  ❌ {service}: {e}")

def send_discord(webhook_url, message):
    """Send Discord notification"""
    payload = {
        "content": message,
        "username": "DB Bot",
        "embeds": [{
            "title": "📊 Database Alert",
            "description": message,
            "color": 3447003,
            "timestamp": datetime.datetime.now().isoformat()
        }]
    }
    send_webhook(webhook_url, payload, "Discord")

def send_slack(webhook_url, message):
    """Send Slack notification"""
    payload = {
        "text": f"📊 Database Alert\n{message}",
        "username": "DB Bot"
    }
    send_webhook(webhook_url, payload, "Slack")

def send_generic(webhook_url, message):
    """Send generic webhook"""
    payload = {
        "service": "database",
        "message": message,
        "timestamp": datetime.datetime.now().isoformat(),
        "host": os.uname().nodename
    }
    send_webhook(webhook_url, payload, "Webhook")

def send_email_alert(smtp_config, to, subject, body):
    """Send email notification (conceptual - needs SMTP lib)"""
    print(f"  📧 Email to {to}: {subject}")

def check_and_notify():
    """Check for conditions that should trigger notifications"""
    conn = get_db()
    c = conn.cursor()
    
    alerts = []
    
    # High priority tasks
    c.execute("SELECT COUNT(*) FROM tasks WHERE priority >= 4 AND done=0")
    high = c.fetchone()[0]
    if high > 0:
        alerts.append(f"🔴 {high} high-priority tasks pending")
    
    # Database size
    size = os.path.getsize(DB_PATH) // 1024
    if size > 1024:
        alerts.append(f"💾 Database is {size}KB")
    
    # Low completion rate
    c.execute("SELECT COUNT(*) FROM tasks")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tasks WHERE done=1")
    done = c.fetchone()[0]
    if total > 0 and done/total < 0.5:
        alerts.append(f"⚠️  Low completion rate: {done/total*100:.0f}%")
    
    conn.close()
    
    if not alerts:
        print("✅ No alerts to send")
        return
    
    # Send notifications
    config = load_webhooks()
    message = "\n".join(alerts)
    
    print(f"\n📢 Sending {len(alerts)} alert(s)...\n")
    
    if config.get("discord"):
        send_discord(config["discord"], message)
    if config.get("slack"):
        send_slack(config["slack"], message)
    if config.get("webhook_url"):
        send_generic(config["webhook_url"], message)
    
    print(f"\n✅ Notifications sent!")

def setup_demo_webhooks():
    """Set up demo webhook configuration"""
    config = {
        "discord": None,  # Add your Discord webhook URL
        "slack": None,    # Add your Slack webhook URL
        "webhook_url": "https://webhook.site/test",
        "email": None
    }
    save_webhooks(config)
    print("✅ Webhook config created at: ~/webhooks.json")
    print("   Edit the file to add your actual webhook URLs")

def main():
    print("\n" + "="*50)
    print("  📢 WEBHOOK NOTIFICATIONS")
    print("="*50)
    
    setup_demo_webhooks()
    check_and_notify()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
System Monitoring Module
- CPU, RAM, Disk monitoring
- Service health checks
- Performance metrics
"""

import os
import time
import sqlite3
import json
import datetime

DB_PATH = os.path.expanduser("~/my-database.db")

def get_system_info():
    """Get system information"""
    info = {}
    
    # Disk usage
    stat = os.statvfs(os.path.expanduser("~"))
    total = stat.f_blocks * stat.f_frsize
    free = stat.f_bfree * stat.f_frsize
    used = total - free
    info['disk'] = {
        'total_gb': total / 1e9,
        'used_gb': used / 1e9,
        'free_gb': free / 1e9,
        'percent': int(used / total * 100) if total > 0 else 0
    }
    
    # Database size
    info['db_size_kb'] = os.path.getsize(DB_PATH) // 1024
    
    # File count
    home = os.path.expanduser("~")
    file_count = sum(len(files) for _, _, files in os.walk(home))
    info['files'] = file_count
    
    return info

def show_system_monitor():
    """Display system monitoring dashboard"""
    print("\n" + "="*50)
    print("  🖥️  SYSTEM MONITOR")
    print("="*50)
    
    info = get_system_info()
    
    # Disk
    disk = info['disk']
    bar = "█" * int(disk['percent'] / 3.33) + "░" * (30 - int(disk['percent'] / 3.33))
    print(f"\n💾 Disk Usage:")
    print(f"   │{bar}│ {disk['percent']}%")
    print(f"   Used:  {disk['used_gb']:.1f} GB")
    print(f"   Free:  {disk['free_gb']:.1f} GB")
    print(f"   Total: {disk['total_gb']:.1f} GB")
    
    # Database
    print(f"\n🗄️  Database:")
    print(f"   Size: {info['db_size_kb']} KB")
    
    # Services
    print(f"\n⚡ Services:")
    services = {
        'dashboard.py': 8888,
        'db-api-server.py': 3000,
        'auto-backup-service.sh': 'backup'
    }
    
    for proc, port in services.items():
        running = False
        for line in os.popen(f"ps aux | grep {proc} | grep -v grep").readlines():
            if proc in line:
                running = True
                break
        
        status = "✅ Running" if running else "❌ Stopped"
        print(f"   {proc:<30} {status}")
    
    # Files
    print(f"\n📁 Files: {info['files']}")
    
    # Uptime
    with open('/proc/uptime', 'r') as f:
        uptime_sec = float(f.readline().split()[0])
    days = int(uptime_sec // 86400)
    hours = int((uptime_sec % 86400) // 3600)
    mins = int((uptime_sec % 3600) // 60)
    print(f"\n⏱️  Uptime: {days}d {hours}h {mins}m")

def monitor_loop(seconds=60):
    """Continuous monitoring"""
    print(f"\n🔄 Monitoring every {seconds}s (Ctrl+C to stop)\n")
    
    try:
        while True:
            show_system_monitor()
            time.sleep(seconds)
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped")

def export_system_status():
    """Export current system status"""
    info = get_system_info()
    info['timestamp'] = datetime.datetime.now().isoformat()
    info['uptime'] = os.popen('uptime').read().strip()
    
    # Service status
    services = {}
    for proc in ['dashboard.py', 'db-api-server.py', 'auto-backup-service.sh']:
        running = False
        for line in os.popen(f"ps aux | grep {proc} | grep -v grep").readlines():
            if proc in line:
                running = True
                break
        services[proc] = running
    info['services'] = services
    
    filename = os.path.expanduser("~/system-status.json")
    with open(filename, 'w') as f:
        json.dump(info, f, indent=2, default=str)
    
    print(f"✅ Status exported to {filename}")

if __name__ == "__main__":
    show_system_monitor()
    export_system_status()

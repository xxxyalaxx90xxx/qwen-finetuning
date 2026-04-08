#!/usr/bin/env python3
"""
Terminal UI (TUI) - Interactive Menu System
Beautiful terminal interface with colors and navigation
"""

import curses
import sqlite3
import os
import datetime

DB_PATH = os.path.expanduser("~/my-database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_RED, -1)
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)
    
    menu_items = [
        ("📊 Dashboard", show_dashboard),
        ("👤 Users", show_users),
        ("📝 Notes", show_notes),
        ("✅ Tasks", show_tasks),
        ("📁 Projects", show_projects),
        ("🤖 AI Insights", show_ai_insights),
        ("⚡ Performance", show_performance),
        ("🔧 Settings", show_settings),
        ("🚪 Exit", None),
    ]
    
    selected = 0
    
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        
        # Header
        title = " DATABASE SYSTEM v3.0 "
        stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(1, (w - len(title)) // 2, title)
        stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        
        # Date
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(2, (w - len(date_str)) // 2, date_str)
        stdscr.attroff(curses.color_pair(3))
        
        # Menu
        start_y = 5
        for i, (name, _) in enumerate(menu_items):
            x = (w - len(name) - 4) // 2
            if i == selected:
                stdscr.attron(curses.color_pair(2) | curses.A_BOLD | curses.A_REVERSE)
                stdscr.addstr(start_y + i, x, f" ▶ {name} ◀ ")
                stdscr.attroff(curses.color_pair(2) | curses.A_BOLD | curses.A_REVERSE)
            else:
                stdscr.addstr(start_y + i, x, f"   {name}   ")
        
        # Footer
        footer = "↑/↓ Navigate | Enter Select | q Quit"
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(h - 2, (w - len(footer)) // 2, footer)
        stdscr.attroff(curses.color_pair(3))
        
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == curses.KEY_UP:
            selected = (selected - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(menu_items)
        elif key in (curses.KEY_ENTER, 10, 13):
            if selected == len(menu_items) - 1:
                break
            _, func = menu_items[selected]
            if func:
                func(stdscr)
        elif key in (ord('q'), ord('Q')):
            break

def show_dashboard(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    conn = get_db()
    c = conn.cursor()
    
    stats = {}
    for t in ['users', 'notes', 'projects', 'tasks']:
        c.execute(f"SELECT COUNT(*) FROM {t}")
        stats[t] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tasks WHERE done=1")
    stats['done'] = c.fetchone()[0]
    
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(2, 2, "📊 DASHBOARD")
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
    
    y = 5
    for name, val in stats.items():
        stdscr.addstr(y, 4, f"{name:<12}: ")
        stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        stdscr.addstr(f"{val}")
        stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
        y += 2
    
    stdscr.addstr(h - 2, 2, "Press any key to return")
    stdscr.refresh()
    stdscr.getch()
    conn.close()

def show_users(stdscr):
    stdscr.clear()
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users ORDER BY id")
    
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(2, 2, "👤 USERS")
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
    
    y = 5
    for r in c.fetchall():
        stdscr.addstr(y, 4, f"#{r['id']} {r['username']:<15} {r['email'] or '':<30} {r['created_at']}")
        y += 2
    
    stdscr.addstr(22, 2, "Press any key to return")
    stdscr.refresh()
    stdscr.getch()
    conn.close()

def show_notes(stdscr):
    stdscr.clear()
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, title, created_at FROM notes ORDER BY id DESC LIMIT 15")
    
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(2, 2, "📝 NOTES")
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
    
    y = 5
    for r in c.fetchall():
        stdscr.addstr(y, 4, f"#{r['id']} {r['title']:<30} {r['created_at']}")
        y += 2
    
    stdscr.addstr(22, 2, "Press any key to return")
    stdscr.refresh()
    stdscr.getch()
    conn.close()

def show_tasks(stdscr):
    stdscr.clear()
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, title, done, priority, created_at FROM tasks ORDER BY priority DESC, id LIMIT 15")
    
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(2, 2, "✅ TASKS")
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
    
    y = 5
    for r in c.fetchall():
        status = "✅" if r['done'] else "⬜"
        pri = "🔴" * r['priority'] + "⚪" * (5 - r['priority'])
        stdscr.addstr(y, 4, f"{status} #{r['id']} {r['title']:<25} P{r['priority']} {r['created_at'][:10]}")
        y += 2
    
    stdscr.addstr(22, 2, "Press any key to return")
    stdscr.refresh()
    stdscr.getch()
    conn.close()

def show_projects(stdscr):
    stdscr.clear()
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT p.*, COUNT(t.id) as tasks FROM projects p LEFT JOIN tasks t ON p.id = t.project_id GROUP BY p.id")
    
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(2, 2, "📁 PROJECTS")
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
    
    y = 5
    for r in c.fetchall():
        stdscr.addstr(y, 4, f"#{r['id']} {r['name']:<25} [{r['status']}] {r['tasks']} tasks")
        y += 2
    
    stdscr.addstr(22, 2, "Press any key to return")
    stdscr.refresh()
    stdscr.getch()
    conn.close()

def show_ai_insights(stdscr):
    stdscr.clear()
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM tasks")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tasks WHERE done=1")
    done = c.fetchone()[0]
    rate = int(done/max(total,1)*100)
    
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(2, 2, "🤖 AI INSIGHTS")
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
    
    insights = []
    if rate >= 80: insights.append(("🌟 Excellent completion rate!", 2))
    elif rate < 50: insights.append(("⚠️ Low completion - focus on tasks", 4))
    
    c.execute("SELECT COUNT(*) FROM tasks WHERE priority >= 4 AND done=0")
    high = c.fetchone()[0]
    if high > 0: insights.append((f"🔴 {high} high-priority pending", 4))
    
    y = 5
    for text, color in insights:
        stdscr.attron(curses.color_pair(color))
        stdscr.addstr(y, 4, text)
        stdscr.attroff(curses.color_pair(color))
        y += 2
    
    stdscr.addstr(22, 2, "Press any key to return")
    stdscr.refresh()
    stdscr.getch()
    conn.close()

def show_performance(stdscr):
    stdscr.clear()
    size = os.path.getsize(DB_PATH) // 1024
    
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(2, 2, "⚡ PERFORMANCE")
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
    
    stdscr.addstr(5, 4, f"Database Size: {size} KB")
    stdscr.addstr(7, 4, f"Status: {'Optimal' if size < 1024 else 'Growing'}")
    
    stdscr.addstr(22, 2, "Press any key to return")
    stdscr.refresh()
    stdscr.getch()

def show_settings(stdscr):
    stdscr.clear()
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(2, 2, "🔧 SETTINGS")
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
    
    stdscr.addstr(5, 4, "DB_PATH: " + DB_PATH)
    stdscr.addstr(7, 4, "Port: 8888 (Dashboard)")
    stdscr.addstr(8, 4, "Port: 3000 (REST API)")
    stdscr.addstr(9, 4, "Backup: Hourly")
    
    stdscr.addstr(22, 2, "Press any key to return")
    stdscr.refresh()
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)

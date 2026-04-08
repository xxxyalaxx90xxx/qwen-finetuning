#!/data/data/com.termux/files/usr/bin/bash
# Qwen System Manager - Unified Menu for All Services
# Usage: bash ~/manager.sh

clear

cat << 'HEADER'
╔══════════════════════════════════════════════╗
║                                              ║
║     ██╗    ██╗██╗███╗   ██╗    ███╗   ███╗   ║
║     ██║    ██║██║████╗  ██║    ████╗ ████║   ║
║     ██║ █╗ ██║██║██╔██╗ ██║    ██╔████╔██║   ║
║     ██║███╗██║██║██║╚██╗██║    ██║╚██╔╝██║   ║
║     ╚███╔███╔╝██║██║ ╚████║    ██║ ╚═╝ ██║   ║
║      ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝    ╚═╝     ╚═╝   ║
║                                              ║
║        System Manager v1.0                   ║
║        Android/Termux Control Center         ║
║                                              ║
╚══════════════════════════════════════════════╝
HEADER

while true; do
    echo ""
    echo "═══════════════════════════════════════════"
    echo "  MAIN MENU"
    echo "═══════════════════════════════════════════"
    echo ""
    echo "  DATABASE"
    echo "  1.  Database CLI"
    echo "  2.  Dashboard v2 (http://localhost:8888)"
    echo "  3.  REST API (http://localhost:3000)"
    echo "  4.  Admin Panel (http://localhost:9090)"
    echo "  5.  Run Backup"
    echo "  6.  View Backups"
    echo ""
    echo "  AI / QWEN"
    echo "  7.  Qwen Chat (Groq)"
    echo "  8.  Qwen Chat (OpenRouter)"
    echo "  9.  Colab Fine-tuning"
    echo "  10. AI Database Assistant"
    echo "  11. AI Auto-Optimizer"
    echo "  12. AI Task Manager"
    echo ""
    echo "  MODS & TUNING"
    echo "  13. Performance Tuning"
    echo "  14. System Self-Tune"
    echo "  15. Full-Text Search"
    echo "  16. Plugin System"
    echo "  17. Import/Export (JSON/XML/YAML/CSV/SQL)"
    echo "  18. Webhook Notifications"
    echo ""
    echo "  TOOLS"
    echo "  19. Security Module"
    echo "  20. Notifications"
    echo "  21. Analytics & Reports"
    echo "  22. System Monitor"
    echo "  23. Terminal UI"
    echo ""
    echo "  SYSTEM"
    echo "  24. GitHub Status"
    echo "  25. Push to GitHub"
    echo "  26. System Info"
    echo "  27. Running Services"
    echo "  28. Start Auto-Backup"
    echo "  29. Stop All Services"
    echo ""
    echo "  0.  Exit"
    echo ""
    echo -n "  Choice: "
    read choice

    case $choice in
        1) python3 ~/database-toolkit.py ;;
        2) termux-open-url http://localhost:8888 2>/dev/null || echo "  http://localhost:8888" ;;
        3) curl -s http://127.0.0.1:3000/api/stats | python3 -m json.tool ;;
        4) termux-open-url http://localhost:9090 2>/dev/null || echo "  http://localhost:9090" ;;
        5) bash ~/backup-db.sh ;;
        6) ls -lh ~/backups/ 2>/dev/null ;;
        7) python3 ~/qwen-chat-groq.py ;;
        8) python3 ~/qwen-chat-openrouter.py ;;
        9) echo "  https://colab.research.google.com/github/xxxyalaxx90xxx/qwen-finetuning/blob/main/colab-finetune.ipynb" ;;
        10) python3 ~/ai-db-assistant.py ;;
        11) python3 ~/auto-optimizer.py ;;
        12) python3 ~/ai-task-manager.py ;;
        13) python3 ~/perf-tuning.py ;;
        14) python3 ~/system-selftune.py ;;
        15) python3 ~/fulltext-search.py ;;
        16) python3 ~/plugin-system.py ;;
        17) python3 ~/data-import-export.py ;;
        18) python3 ~/webhook-notifications.py ;;
        19) python3 ~/security.py ;;
        20) python3 ~/notifications.py ;;
        21) python3 ~/analytics.py ;;
        22) python3 ~/system-monitor.py ;;
        23) python3 ~/terminal-tui.py ;;
        24) cd ~/qwen-finetuning && git log --oneline -5 && echo "" && git status --short ;;
        25) cd ~/qwen-finetuning && git add -A && git commit -m "Auto commit" && git push origin main 2>&1 | tail -3 ;;
        26) uname -a; df -h ~ | tail -1; python3 --version; git --version ;;
        27) ps aux | grep -E "python3|bash" | grep -v grep | awk '{printf "  PID: %s | %s\n", $2, $11}' ;;
        28) pkill -f auto-backup-service.sh 2>/dev/null; bash ~/auto-backup-service.sh &; echo "  Auto-backup started" ;;
        29) pkill -f dashboard 2>/dev/null; pkill -f db-api-server 2>/dev/null; pkill -f admin-panel 2>/dev/null; pkill -f auto-backup 2>/dev/null; echo "  All stopped" ;;
        0) echo "  Bye!"; exit 0 ;;
        *) echo "  Invalid choice" ;;
    esac

    echo ""
    echo "  Press Enter to continue..."
    read
    clear
done

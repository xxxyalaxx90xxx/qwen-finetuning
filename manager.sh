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
    echo "  1. Open Database CLI"
    echo "  2. View Dashboard (http://localhost:8888)"
    echo "  3. Start REST API (http://localhost:3000)"
    echo "  4. Run Backup"
    echo "  5. View Backups"
    echo ""
    echo "  AI / QWEN"
    echo "  6. Qwen Chat (Groq)"
    echo "  7. Qwen Chat (OpenRouter)"
    echo "  8. Open Colab Fine-tuning"
    echo "  9. AI Database Assistant"
    echo ""
    echo "  MODS & TUNING"
    echo "  10. Performance Tuning"
    echo "  11. Security Module"
    echo "  12. Notifications"
    echo "  13. Analytics & Reports"
    echo "  14. System Monitor"
    echo ""
    echo "  GITHUB"
    echo "  15. View Repo Status"
    echo "  16. Push Changes"
    echo ""
    echo "  SYSTEM"
    echo "  17. System Info"
    echo "  18. Running Services"
    echo "  19. Start Auto-Backup"
    echo "  20. Stop All Services"
    echo ""
    echo "  0. Exit"
    echo ""
    echo -n "  Choice: "
    read choice

    case $choice in
        1) python3 ~/database-toolkit.py ;;
        2) termux-open-url http://localhost:8888 2>/dev/null || echo "  http://localhost:8888" ;;
        3) pkill -f db-api-server.py 2>/dev/null; python3 ~/db-api-server.py &; echo "  API started" ;;
        4) bash ~/backup-db.sh ;;
        5) ls -lh ~/backups/ 2>/dev/null || echo "  No backups" ;;
        6) python3 ~/qwen-chat-groq.py ;;
        7) python3 ~/qwen-chat-openrouter.py ;;
        8) echo "  https://colab.research.google.com/github/xxxyalaxx90xxx/qwen-finetuning/blob/main/colab-finetune.ipynb" ;;
        9) python3 ~/ai-db-assistant.py ;;
        10) python3 ~/perf-tuning.py ;;
        11) python3 ~/security.py ;;
        12) python3 ~/notifications.py ;;
        13) python3 ~/analytics.py ;;
        14) python3 ~/system-monitor.py ;;
        15) cd ~/qwen-finetuning && git log --oneline -3 && echo "" && git status --short ;;
        16) cd ~/qwen-finetuning && git add -A && git commit -m "Auto commit" && git push origin main 2>&1 | tail -3 ;;
        17) echo ""; uname -a; echo "  Disk: $(df -h ~ | tail -1 | awk '{print $4}') free"; python3 --version; git --version ;;
        18) echo ""; ps aux | grep -E "python3|bash" | grep -v grep | awk '{printf "  PID: %s | %s\n", $2, $11}' ;;
        19) pkill -f auto-backup-service.sh 2>/dev/null; bash ~/auto-backup-service.sh &; echo "  Auto-backup started" ;;
        20) pkill -f dashboard.py 2>/dev/null; pkill -f db-api-server.py 2>/dev/null; pkill -f auto-backup-service.sh 2>/dev/null; echo "  All stopped" ;;
        0) echo "  Bye!"; exit 0 ;;
        *) echo "  Invalid choice" ;;
    esac

    echo ""
    echo "  Press Enter to continue..."
    read
    clear
done

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
    echo ""
    echo "  GITHUB"
    echo "  9. View Repo Status"
    echo "  10. Push Changes"
    echo ""
    echo "  SYSTEM"
    echo "  11. System Info"
    echo "  12. Running Services"
    echo "  13. Stop All Services"
    echo ""
    echo "  0. Exit"
    echo ""
    echo -n "  Choice: "
    read choice

    case $choice in
        1) python3 ~/database-toolkit.py ;;
        2)
            echo ""
            echo "  Dashboard: http://localhost:8888"
            echo "  Open in browser: termux-open-url http://localhost:8888"
            termux-open-url http://localhost:8888 2>/dev/null || open http://localhost:8888 2>/dev/null || echo "  URL: http://localhost:8888"
            ;;
        3)
            pkill -f db-api-server.py 2>/dev/null
            python3 ~/db-api-server.py &
            echo "  API started on port 3000"
            ;;
        4) bash ~/backup-db.sh ;;
        5)
            echo ""
            echo "  Backups:"
            ls -lh ~/backups/ 2>/dev/null || echo "  No backups found"
            ;;
        6) python3 ~/qwen-chat-groq.py ;;
        7) python3 ~/qwen-chat-openrouter.py ;;
        8) echo "  https://colab.research.google.com/github/xxxyalaxx90xxx/qwen-finetuning/blob/main/colab-finetune.ipynb" ;;
        9)
            echo ""
            cd ~/qwen-finetuning && git log --oneline -3 && echo ""
            git status --short
            ;;
        10)
            cd ~/qwen-finetuning && git add -A && git commit -m "Auto commit" && git push origin main 2>&1 | tail -3
            ;;
        11)
            echo ""
            echo "  OS: $(uname -a)"
            echo "  CPU: $(uname -m)"
            echo "  Uptime: $(uptime)"
            echo "  Disk: $(df -h ~ | tail -1 | awk '{print $4}') free"
            echo "  Python: $(python3 --version 2>&1)"
            echo "  Git: $(git --version 2>&1)"
            ;;
        12)
            echo ""
            echo "  Running Python services:"
            ps aux | grep "python3" | grep -v grep || echo "  None"
            echo ""
            echo "  Ports in use:"
            ss -tlnp 2>/dev/null | grep -E "8888|3000" || netstat -tlnp 2>/dev/null | grep -E "8888|3000" || echo "  Unable to check ports"
            ;;
        13)
            pkill -f dashboard.py 2>/dev/null
            pkill -f db-api-server.py 2>/dev/null
            echo "  All services stopped"
            ;;
        0) echo "  Bye!"; exit 0 ;;
        *) echo "  Invalid choice" ;;
    esac

    echo ""
    echo "  Press Enter to continue..."
    read
    clear
done

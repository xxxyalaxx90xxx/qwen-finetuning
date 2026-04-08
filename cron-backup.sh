#!/data/data/com.termux/files/usr/bin/bash
# Auto-backup every hour using Termux:Tasker or cron
# Add to crontab: 0 * * * * bash ~/cron-backup.sh

LOG="$HOME/backups/backup.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Running auto-backup..." >> "$LOG"
bash ~/backup-db.sh >> "$LOG" 2>&1
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Done" >> "$LOG"
echo "---" >> "$LOG"

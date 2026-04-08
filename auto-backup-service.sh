#!/data/data/com.termux/files/usr/bin/bash
# Background auto-backup service
# Run: bash ~/auto-backup-service.sh &
# Stop: pkill -f auto-backup-service

echo "🔄 Auto-backup service started (every 1 hour)"
echo "   Stop with: pkill -f auto-backup-service"
echo ""

while true; do
    bash ~/cron-backup.sh 2>&1
    echo "⏳ Next backup in 1 hour... (press Ctrl+C to stop)"
    sleep 3600
done

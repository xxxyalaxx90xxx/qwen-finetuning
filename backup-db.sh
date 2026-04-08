#!/bin/bash
# Automated Database Backup Script
# Run manually or schedule with cron
# Usage: bash ~/backup-db.sh

set -e

DB_PATH="$HOME/my-database.db"
BACKUP_DIR="$HOME/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/db-backup-$TIMESTAMP.db"
JSON_FILE="$BACKUP_DIR/db-export-$TIMESTAMP.json"

mkdir -p "$BACKUP_DIR"

# Binary backup
if [ -f "$DB_PATH" ]; then
    cp "$DB_PATH" "$BACKUP_FILE"
    echo "Binary backup: $BACKUP_FILE"
else
    echo "No database found at $DB_PATH"
    exit 1
fi

# JSON export
python3 -c "
import sqlite3, json, os
conn = sqlite3.connect('$DB_PATH')
conn.row_factory = sqlite3.Row
data = {}
for t in ['users','notes','projects','tasks']:
    c = conn.cursor()
    c.execute(f'SELECT * FROM {t}')
    data[t] = [dict(r) for r in c.fetchall()]
with open('$JSON_FILE', 'w') as f:
    json.dump(data, f, indent=2, default=str)
conn.close()
print('JSON export: $JSON_FILE')
"

# Cleanup old backups (keep last 10)
cd "$BACKUP_DIR"
ls -t *.db 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null
ls -t *.json 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null

echo ""
echo "Backup complete!"
echo "Location: $BACKUP_DIR"
echo "Total backups: $(ls "$BACKUP_DIR"/*.db 2>/dev/null | wc -l)"

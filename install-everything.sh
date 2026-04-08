#!/bin/bash
# Complete Installation Guide for Android/Termux
# Run: bash ~/install-everything.sh

set -e

echo "╔══════════════════════════════════════════╗"
echo "║  Termux Complete Installation Script     ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ─── Step 1: Update packages ───
echo "📦 Step 1: Updating packages..."
pkg update -y 2>&1 | tail -3
echo "✅ Done"

# ─── Step 2: Install base tools ───
echo ""
echo "🔧 Step 2: Installing base tools..."
pkg install -y git curl wget jq tree sqlite3 2>&1 | tail -3
echo "✅ Done"

# ─── Step 3: Install Python packages (no pip needed - using only builtins) ───
echo ""
echo "🐍 Step 3: Python3 is already installed"
python3 --version

# ─── Step 4: Setup Database Toolkit ───
echo ""
echo "🗄️ Step 4: Database toolkit ready..."
python3 -c "import sqlite3; print('✅ SQLite3:', sqlite3.sqlite_version)"

# ─── Step 5: Setup GitHub repos ───
echo ""
echo "📁 Step 5: GitHub repos..."
ls -d ~/redis 2>/dev/null && echo "✅ Redis cloned (29 MB)" || echo "❌ Redis not found"
ls -d ~/chroma 2>/dev/null && echo "✅ Chroma cloned (70 MB)" || echo "❌ Chroma not found"

# ─── Step 6: Create aliases ───
echo ""
echo "🔗 Step 6: Creating aliases..."

cat >> ~/.bashrc << 'EOF'

# ─── Qwen Database Toolkit ───
alias db='python3 ~/database-toolkit.py'
alias db-chat='python3 ~/database-toolkit.py'
alias db-stats='python3 -c "
import sqlite3, os
conn = sqlite3.connect(os.path.expanduser(\"~/my-database.db\"))
c = conn.cursor()
for t in [\"users\",\"notes\",\"projects\",\"tasks\"]:
    c.execute(f\"SELECT COUNT(*) FROM {t}\")
    print(f\"  {t}: {c.fetchone()[0]} rows\")
conn.close()
"'
alias db-export='python3 -c "
import sqlite3, json, os
conn = sqlite3.connect(os.path.expanduser(\"~/my-database.db\"))
conn.row_factory = sqlite3.Row
data = {}
for t in [\"users\",\"notes\",\"projects\",\"tasks\"]:
    c = conn.cursor()
    c.execute(f\"SELECT * FROM {t}\")
    data[t] = [dict(r) for r in c.fetchall()]
with open(os.path.expanduser(\"~/database-export.json\"), \"w\") as f:
    json.dump(data, f, indent=2)
print(\"Exported to ~/database-export.json\")
conn.close()
"'
EOF

echo "✅ Aliases added to ~/.bashrc"

# ─── Step 7: Create quick start guide ───
echo ""
echo "📖 Step 7: Creating quick start guide..."

cat > ~/README.md << 'EOF'
# Termux Setup Complete

## Database Toolkit
```bash
db                    # Open interactive database
db-stats              # Show statistics
db-export             # Export to JSON
```

## Database Commands
```
add-user name email   # Add user
list-users            # List all users
add-note title text   # Add note
list-notes            # List notes
search-notes keyword  # Search notes
add-project name      # Create project
list-projects         # List projects
add-task project title # Add task
list-tasks            # List tasks
complete-task id      # Mark task done
export                # Export to JSON
stats                 # Show statistics
quit                  # Exit
```

## Chat with AI (need API key)
```bash
python3 ~/qwen-chat-groq.py      # Groq (free)
python3 ~/qwen-chat-openrouter.py # OpenRouter
```

## GitHub Repos
```
~/redis/     - In-memory database source
~/chroma/    - Vector database source
```

## Fine-Tuning (Cloud only)
👉 https://colab.research.google.com/github/xxxyalaxx90xxx/qwen-finetuning/blob/main/colab-finetune.ipynb
EOF

echo "✅ Quick start guide created: ~/README.md"

# ─── Done ───
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  ✅ Installation Complete!               ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "Quick start:"
echo "  db          → Open database"
echo "  db-stats    → Show stats"
echo "  cat ~/README.md  → Full guide"
echo ""
echo "Restart terminal for aliases to work:"
echo "  source ~/.bashrc"

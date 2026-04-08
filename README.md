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

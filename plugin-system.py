#!/usr/bin/env python3
"""
Plugin System - Extensible Architecture
Load, manage, and run plugins dynamically
"""

import os
import json
import importlib.util
import importlib
import datetime

PLUGIN_DIR = os.path.expanduser("~/plugins")
PLUGIN_CONFIG = os.path.expanduser("~/plugins-config.json")

# ═══════════════════════════════════════════
# Plugin Manager
# ═══════════════════════════════════════════

class PluginManager:
    def __init__(self):
        self.plugins = {}
        self.config = self.load_config()
        os.makedirs(PLUGIN_DIR, exist_ok=True)
    
    def load_config(self):
        if os.path.exists(PLUGIN_CONFIG):
            with open(PLUGIN_CONFIG, 'r') as f:
                return json.load(f)
        return {"enabled": [], "disabled": []}
    
    def save_config(self):
        with open(PLUGIN_CONFIG, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def discover_plugins(self):
        """Find all available plugins"""
        plugins = []
        if os.path.exists(PLUGIN_DIR):
            for f in os.listdir(PLUGIN_DIR):
                if f.endswith('.py') and not f.startswith('_'):
                    plugins.append(f[:-3])
        return plugins
    
    def load_plugin(self, name):
        """Load a plugin"""
        plugin_path = os.path.join(PLUGIN_DIR, f"{name}.py")
        if not os.path.exists(plugin_path):
            print(f"❌ Plugin '{name}' not found")
            return None
        
        try:
            spec = importlib.util.spec_from_file_location(name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'run'):
                self.plugins[name] = module
                print(f"✅ Loaded plugin: {name}")
                return module
            else:
                print(f"⚠️  Plugin '{name}' has no run() function")
                return None
        except Exception as e:
            print(f"❌ Failed to load '{name}': {e}")
            return None
    
    def enable_plugin(self, name):
        if name not in self.config["enabled"]:
            self.config["enabled"].append(name)
            if name in self.config["disabled"]:
                self.config["disabled"].remove(name)
            self.save_config()
        print(f"✅ Enabled plugin: {name}")
    
    def disable_plugin(self, name):
        if name in self.config["enabled"]:
            self.config["enabled"].remove(name)
            self.config["disabled"].append(name)
            self.save_config()
        print(f"⏸️  Disabled plugin: {name}")
    
    def run_plugin(self, name, *args, **kwargs):
        if name in self.plugins:
            return self.plugins[name].run(*args, **kwargs)
        module = self.load_plugin(name)
        if module and hasattr(module, 'run'):
            return module.run(*args, **kwargs)
    
    def run_all(self):
        for name in self.config["enabled"]:
            print(f"\n▶️  Running plugin: {name}")
            self.run_plugin(name)
    
    def list_plugins(self):
        available = self.discover_plugins()
        print(f"\n📦 Plugins ({len(available)} available)\n")
        for p in available:
            status = "✅" if p in self.config["enabled"] else "⏸️"
            print(f"  {status} {p}")
        
        if not available:
            print("  No plugins found. Create .py files in ~/plugins/")

# ═══════════════════════════════════════════
# Built-in Plugins
# ═══════════════════════════════════════════

def install_sample_plugins():
    """Install sample plugins"""
    os.makedirs(PLUGIN_DIR, exist_ok=True)
    
    # Plugin 1: Hello World
    with open(os.path.join(PLUGIN_DIR, "hello.py"), 'w') as f:
        f.write('''
def run():
    print("  👋 Hello from plugin!")
    print(f"  📅 {__import__("datetime").datetime.now()}")
''')
    
    # Plugin 2: DB Stats
    with open(os.path.join(PLUGIN_DIR, "db_stats.py"), 'w') as f:
        f.write('''
def run():
    import sqlite3, os
    db = os.path.expanduser("~/my-database.db")
    conn = sqlite3.connect(db)
    c = conn.cursor()
    for t in ["users", "notes", "projects", "tasks"]:
        c.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"  {t}: {c.fetchone()[0]}")
    conn.close()
''')
    
    # Plugin 3: System Info
    with open(os.path.join(PLUGIN_DIR, "sysinfo.py"), 'w') as f:
        f.write('''
def run():
    import os, platform
    print(f"  OS: {platform.system()} {platform.release()}")
    print(f"  Python: {platform.python_version()}")
    home = os.path.expanduser("~")
    files = sum(len(files) for _, _, files in os.walk(home))
    print(f"  Files: {files}")
''')
    
    print("✅ Installed 3 sample plugins")

def main():
    print("\n" + "="*50)
    print("  📦 PLUGIN SYSTEM")
    print("="*50)
    
    pm = PluginManager()
    
    # Install sample plugins
    print("\n📥 Installing sample plugins...")
    install_sample_plugins()
    
    # Discover and enable
    print("\n🔍 Discovering plugins...")
    pm.list_plugins()
    
    for plugin in pm.discover_plugins():
        pm.enable_plugin(plugin)
        pm.load_plugin(plugin)
    
    # Run all enabled plugins
    print("\n▶️  Running all plugins...\n")
    pm.run_all()
    
    print("\n✅ Plugin system complete!")

if __name__ == "__main__":
    main()

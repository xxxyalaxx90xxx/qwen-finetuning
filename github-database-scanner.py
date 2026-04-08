#!/usr/bin/env python3
"""
GitHub Database Scanner
Search GitHub for databases, datasets, and data repositories
"""

import httpx
import json
import sys

GITHUB_API = "https://api.github.com/search/repositories"

def search_github(query, sort="stars", order="desc", per_page=10, page=1):
    """Search GitHub repositories"""
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    # Try with token if available
    import os
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    
    params = {
        "q": query,
        "sort": sort,
        "order": order,
        "per_page": per_page,
        "page": page,
    }
    
    try:
        resp = httpx.get(GITHUB_API, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def display_results(data):
    """Display search results"""
    if not data or "items" not in data:
        print("No results found.")
        return
    
    total = data.get("total_count", 0)
    print(f"\nFound {total} repositories\n")
    print("=" * 70)
    
    for i, repo in enumerate(data["items"], 1):
        print(f"\n{i}. {repo['full_name']}")
        print(f"   ⭐ {repo['stargazers_count']}  |  🍴 {repo['forks_count']}  |  📡 {repo.get('language', 'N/A')}")
        print(f"   📄 {repo['description'] or 'No description'}")
        print(f"   🔗 {repo['html_url']}")
        print(f"   📅 Updated: {repo['updated_at'][:10]}")

def main():
    print("\n" + "="*70)
    print("  GitHub Database Scanner")
    print("="*70)
    
    # Predefined search queries
    searches = {
        "1": ("databases dataset", "Most popular database datasets"),
        "2": ("awesome-database", "Awesome database lists"),
        "3": ("sql-database tutorial", "SQL database tutorials"),
        "4": ("machine-learning dataset", "ML/AI datasets"),
        "5": ("public-database", "Public/open databases"),
        "6": ("Custom search", "Enter your own query"),
    }
    
    print("\nChoose search:")
    for k, (q, desc) in searches.items():
        print(f"  {k}. {desc} ({q})")
    
    choice = input("\nChoice (1-6) [1]: ").strip() or "1"
    
    if choice == "6":
        query = input("Search query: ").strip()
        if not query:
            print("No query provided.")
            return
    else:
        query = searches[choice][0]
    
    count = input("Results count (10) [10]: ").strip() or "10"
    
    print(f"\n🔍 Searching: {query}")
    data = search_github(query, per_page=int(count))
    display_results(data)
    
    # Save results
    if data and "items" in data:
        save = input("\nSave to file? (y/n) [n]: ").strip().lower()
        if save == "y":
            filename = f"github-results-{query.replace(' ', '-')}.json"
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Saved to {filename}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Sync repository descriptions and topics to GitHub using the GitHub API.

This script:
1. Reads the manifest.json file
2. For each repository, updates the GitHub description and topics
3. Uses the GitHub REST API to make the updates
4. Handles authentication and rate limiting

Usage:
    python3 scripts/sync_github_repos.py [--dry-run] [--repo REPO_NAME] [--token GITHUB_TOKEN]
    
Options:
    --dry-run        Show what would be changed without making changes
    --repo NAME      Only update a specific repository by name
    --token TOKEN    GitHub personal access token (or set GITHUB_TOKEN env var)
"""

import json
import sys
import argparse
import requests
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

def load_manifest() -> Dict:
    """Load and parse the manifest.json file."""
    manifest_path = Path("manifest.json")
    if not manifest_path.exists():
        print("ERROR: manifest.json not found in current directory")
        sys.exit(1)
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to parse manifest.json: {e}")
        sys.exit(1)

def get_github_token() -> str:
    """Get GitHub token from environment variable or user input."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("ERROR: GitHub token not found. Please set GITHUB_TOKEN environment variable or use --token")
        print("You can create a token at: https://github.com/settings/tokens")
        print("Required scopes: repo (for private repos) or public_repo (for public repos)")
        sys.exit(1)
    return token

def get_repo_owner_and_name(repo_url: str) -> tuple[str, str]:
    """Extract owner and repository name from GitHub URL."""
    # Handle both https://github.com/owner/repo and https://github.com/owner/repo.git
    url = repo_url.rstrip('/')
    if url.endswith('.git'):
        url = url[:-4]  # Remove '.git' suffix
    parts = url.split('/')
    if len(parts) >= 2:
        owner = parts[-2]
        repo_name = parts[-1]
        return owner, repo_name
    raise ValueError(f"Invalid GitHub URL: {repo_url}")

def get_repo_info(owner: str, repo_name: str, token: str) -> Optional[Dict]:
    """Get current repository information from GitHub API."""
    url = f"https://api.github.com/repos/{owner}/{repo_name}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"WARNING: Repository {owner}/{repo_name} not found on GitHub")
            return None
        else:
            print(f"ERROR: Failed to get repo info for {owner}/{repo_name}: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"ERROR: Exception getting repo info for {owner}/{repo_name}: {e}")
        return None

def update_repo_description(owner: str, repo_name: str, description: str, token: str, dry_run: bool = False) -> bool:
    """Update repository description on GitHub."""
    if dry_run:
        print(f"WOULD UPDATE description for {owner}/{repo_name}: '{description}'")
        return True
    
    url = f"https://api.github.com/repos/{owner}/{repo_name}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "description": description
    }
    
    try:
        response = requests.patch(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"✅ Updated description for {owner}/{repo_name}")
            return True
        else:
            print(f"ERROR: Failed to update description for {owner}/{repo_name}: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: Exception updating description for {owner}/{repo_name}: {e}")
        return False

def update_repo_topics(owner: str, repo_name: str, topics: List[str], token: str, dry_run: bool = False) -> bool:
    """Update repository topics on GitHub."""
    if dry_run:
        print(f"WOULD UPDATE topics for {owner}/{repo_name}: {topics}")
        return True
    
    url = f"https://api.github.com/repos/{owner}/{repo_name}/topics"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.mercy-preview+json"
    }
    
    data = {
        "names": topics
    }
    
    try:
        response = requests.put(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"✅ Updated topics for {owner}/{repo_name}")
            return True
        else:
            print(f"ERROR: Failed to update topics for {owner}/{repo_name}: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: Exception updating topics for {owner}/{repo_name}: {e}")
        return False

def sync_repo_to_github(repo_data: Dict, token: str, dry_run: bool = False) -> bool:
    """Sync a single repository to GitHub."""
    repo_name = repo_data.get('name')
    repo_url = repo_data.get('url')
    description = repo_data.get('short_description', '')
    topics = repo_data.get('topics', [])
    
    if not repo_name or not repo_url:
        print(f"WARNING: Repository missing name or URL, skipping")
        return False
    
    if not description:
        print(f"WARNING: Repository '{repo_name}' missing short_description, skipping")
        return False
    
    try:
        owner, github_repo_name = get_repo_owner_and_name(repo_url)
    except ValueError as e:
        print(f"ERROR: {e}")
        return False
    
    # Check if repository exists on GitHub
    repo_info = get_repo_info(owner, github_repo_name, token)
    if not repo_info:
        return False
    
    print(f"\n🔄 Syncing {owner}/{github_repo_name}...")
    
    # Update description
    current_desc = repo_info.get('description', '')
    if current_desc != description:
        success_desc = update_repo_description(owner, github_repo_name, description, token, dry_run)
    else:
        print(f"✅ Description already up to date for {owner}/{github_repo_name}")
        success_desc = True
    
    # Update topics
    current_topics = []
    topics_data = repo_info.get('topics', [])
    if isinstance(topics_data, list):
        current_topics = [topic['name'] if isinstance(topic, dict) else str(topic) for topic in topics_data]
    if set(current_topics) != set(topics):
        success_topics = update_repo_topics(owner, github_repo_name, topics, token, dry_run)
    else:
        print(f"✅ Topics already up to date for {owner}/{github_repo_name}")
        success_topics = True
    
    return success_desc and success_topics

def main():
    parser = argparse.ArgumentParser(description='Sync repository descriptions and topics to GitHub')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without making changes')
    parser.add_argument('--repo', type=str, 
                       help='Only update a specific repository by name')
    parser.add_argument('--token', type=str, 
                       help='GitHub personal access token (or set GITHUB_TOKEN env var)')
    
    args = parser.parse_args()
    
    # Get GitHub token
    token = args.token or get_github_token()
    
    # Load manifest
    manifest = load_manifest()
    repositories = manifest.get('repositories', [])
    
    if not repositories:
        print("ERROR: No repositories found in manifest")
        sys.exit(1)
    
    # Filter repositories if specific repo requested
    if args.repo:
        repositories = [r for r in repositories if r.get('name') == args.repo]
        if not repositories:
            print(f"ERROR: Repository '{args.repo}' not found in manifest")
            sys.exit(1)
    
    # Process each repository
    updated_count = 0
    total_count = len(repositories)
    
    print(f"{'DRY RUN: ' if args.dry_run else ''}Syncing GitHub repositories for {total_count} repositories...")
    print("=" * 60)
    
    for repo in repositories:
        repo_name = repo.get('name')
        if not repo_name:
            print(f"WARNING: Repository missing name, skipping")
            continue
        
        if sync_repo_to_github(repo, token, args.dry_run):
            updated_count += 1
        
        # Add a small delay to respect rate limits
        if not args.dry_run:
            time.sleep(0.5)
    
    print("\n" + "=" * 60)
    if args.dry_run:
        print(f"DRY RUN COMPLETE: Would sync {updated_count}/{total_count} repositories")
    else:
        print(f"✅ COMPLETE: Synced {updated_count}/{total_count} repositories")
    
    if updated_count == 0 and not args.dry_run:
        print("All repositories are already up to date!")

if __name__ == "__main__":
    main()

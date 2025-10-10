#!/usr/bin/env python3
"""
Sync roadmap milestones from repository README files back to manifest.json.

This script:
1. Scans all repository README files for roadmap tables
2. Extracts milestone information (title, category, target date, status)
3. Updates the manifest.json milestones section
4. Preserves existing milestone IDs and structure

Usage:
    python3 scripts/sync_roadmaps_to_manifest.py [--dry-run] [--repo REPO_NAME]
    
Options:
    --dry-run    Show what would be changed without making changes
    --repo NAME  Only sync a specific repository by name
"""

import json
import sys
import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Repository name to workspace path mapping
REPO_PATHS = {
    "ml-foundations": "../ml-foundations",
    "phishing-classifier": "../projects/phishing-classifier", 
    "secure-ai-api": "../projects/secure-ai-api",
    "ai-chat-rag": "../projects/ai-chat-rag",
    "flutter-iam": "../projects/flutter-iam",
    "api-showcase": "../projects/api-showcase",
    "ai-cyber-security-roadmap": "."  # This repo itself
}

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

def save_manifest(manifest: Dict) -> bool:
    """Save the updated manifest.json file."""
    try:
        with open("manifest.json", 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"ERROR: Failed to save manifest.json: {e}")
        return False

def parse_roadmap_table(content: str) -> List[Dict]:
    """
    Parse roadmap table from README content.
    Returns list of milestone dictionaries.
    """
    milestones = []
    
    # Look for the roadmap section - try multiple patterns
    patterns = [
        r'## 🗓 Roadmap\s*\n(.*?)(?=\n---|\n## |\Z)',
        r'## 🗓 Roadmap\s*\n(.*?)(?=\n---|\n##)',
        r'🗓 Roadmap\s*\n(.*?)(?=\n---|\n##)',
    ]
    
    table_content = None
    for pattern in patterns:
        roadmap_match = re.search(pattern, content, re.DOTALL)
        if roadmap_match:
            table_content = roadmap_match.group(1)
            break
    
    if not table_content:
        return milestones
    
    # Parse table rows
    lines = table_content.strip().split('\n')
    in_table = False
    headers = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a table header row
        if '|' in line and ('Milestone' in line or 'Category' in line):
            in_table = True
            # Extract headers
            headers = [col.strip() for col in line.split('|') if col.strip()]
            continue
            
        # Check if this is a separator row (contains dashes)
        if in_table and '---' in line:
            continue
            
        # Parse data rows
        if in_table and '|' in line and not '---' in line:
            parts = [col.strip() for col in line.split('|') if col.strip()]
            if len(parts) >= 3:  # At least milestone, category/date, status
                milestone = {}
                
                # Handle different table formats
                if len(parts) == 3:  # Old format: Milestone | Date | Status
                    milestone['title'] = parts[0]
                    milestone['due'] = parts[1]
                    milestone['status'] = parts[2]
                    milestone['category'] = None
                elif len(parts) == 4:  # New format: Milestone | Category | Date | Status
                    milestone['title'] = parts[0]
                    milestone['category'] = parts[1]
                    milestone['due'] = parts[2]
                    milestone['status'] = parts[3]
                
                # Clean up status indicators
                status = milestone['status']
                if '✅' in status or 'Done' in status:
                    milestone['status'] = 'done'
                elif '⏳' in status or 'Pending' in status or 'In Progress' in status:
                    milestone['status'] = 'in_progress'
                elif 'Planned' in status or 'Todo' in status:
                    milestone['status'] = 'todo'
                else:
                    milestone['status'] = 'todo'  # Default
                
                milestones.append(milestone)
    
    return milestones

def extract_milestones_from_readme(repo_path: Path, repo_name: str) -> List[Dict]:
    """Extract milestones from a repository's README file."""
    readme_path = repo_path / "README.md"
    
    if not readme_path.exists():
        print(f"WARNING: README not found for '{repo_name}' at {readme_path}")
        return []
    
    try:
        content = readme_path.read_text(encoding='utf-8')
        milestones = parse_roadmap_table(content)
        
        # Add repo name to each milestone
        for milestone in milestones:
            milestone['repo'] = repo_name
            
        return milestones
    except Exception as e:
        print(f"ERROR: Failed to read {readme_path}: {e}")
        return []

def update_manifest_milestones(manifest: Dict, new_milestones: List[Dict], dry_run: bool = False) -> int:
    """
    Update manifest milestones with new data from README files.
    Returns number of milestones updated.
    """
    updated_count = 0
    existing_milestones = manifest.get('milestones', [])
    
    # Create a mapping of existing milestones by repo and title
    existing_by_repo_title = {}
    for milestone in existing_milestones:
        key = f"{milestone.get('repo', '')}:{milestone.get('title', '')}"
        existing_by_repo_title[key] = milestone
    
    # Also create a mapping by repo only for partial matches
    existing_by_repo = {}
    for milestone in existing_milestones:
        repo = milestone.get('repo', '')
        if repo not in existing_by_repo:
            existing_by_repo[repo] = []
        existing_by_repo[repo].append(milestone)
    
    for new_milestone in new_milestones:
        repo = new_milestone.get('repo', '')
        title = new_milestone.get('title', '')
        key = f"{repo}:{title}"
        
        # Try exact match first
        if key in existing_by_repo_title:
            existing = existing_by_repo_title[key]
        else:
            # Try partial matching within the same repo
            existing = None
            if repo in existing_by_repo:
                for existing_milestone in existing_by_repo[repo]:
                    # Check if titles are similar (contain similar words)
                    existing_title = existing_milestone.get('title', '').lower()
                    new_title = title.lower()
                    
                    # Check for common patterns
                    if (('scaffold' in existing_title and 'scaffold' in new_title) or
                        ('integration' in existing_title and 'integration' in new_title) or
                        ('auth' in existing_title and 'auth' in new_title) or
                        ('docker' in existing_title and 'docker' in new_title) or
                        ('jwt' in existing_title and 'jwt' in new_title)):
                        existing = existing_milestone
                        break
            
            if not existing:
                # No match found, will add as new
                existing = None
        
        if existing:
            # Update existing milestone
            
            # Update fields if they've changed
            changes = []
            if new_milestone.get('category') and existing.get('category') != new_milestone['category']:
                existing['category'] = new_milestone['category']
                changes.append(f"category: {existing.get('category')} -> {new_milestone['category']}")
            
            if new_milestone.get('due') and existing.get('due') != new_milestone['due']:
                existing['due'] = new_milestone['due']
                changes.append(f"due: {existing.get('due')} -> {new_milestone['due']}")
            
            if new_milestone.get('status') and existing.get('status') != new_milestone['status']:
                existing['status'] = new_milestone['status']
                changes.append(f"status: {existing.get('status')} -> {new_milestone['status']}")
            
            if changes:
                updated_count += 1
                if dry_run:
                    print(f"WOULD UPDATE {repo}: {title}")
                    for change in changes:
                        print(f"  {change}")
                else:
                    print(f"✅ Updated {repo}: {title}")
                    for change in changes:
                        print(f"  {change}")
        else:
            # Add new milestone (this shouldn't happen often)
            if dry_run:
                print(f"WOULD ADD NEW {repo}: {title}")
            else:
                print(f"➕ Added new {repo}: {title}")
                # Generate a new ID
                new_id = f"{repo.split('-')[0]}-{len(existing_milestones) + 1:02d}"
                new_milestone['id'] = new_id
                existing_milestones.append(new_milestone)
                updated_count += 1
    
    return updated_count

def main():
    parser = argparse.ArgumentParser(description='Sync roadmap milestones from README files to manifest')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without making changes')
    parser.add_argument('--repo', type=str, 
                       help='Only sync a specific repository by name')
    
    args = parser.parse_args()
    
    # Load manifest
    manifest = load_manifest()
    
    # Get repositories to process
    repositories = manifest.get('repositories', [])
    if args.repo:
        repositories = [r for r in repositories if r.get('name') == args.repo]
        if not repositories:
            print(f"ERROR: Repository '{args.repo}' not found in manifest")
            sys.exit(1)
    
    # Extract milestones from all repositories
    all_milestones = []
    for repo in repositories:
        repo_name = repo.get('name')
        if not repo_name or repo_name not in REPO_PATHS:
            continue
            
        repo_path = Path(REPO_PATHS[repo_name])
        milestones = extract_milestones_from_readme(repo_path, repo_name)
        all_milestones.extend(milestones)
        print(f"Found {len(milestones)} milestones in {repo_name}")
    
    if not all_milestones:
        print("No milestones found in any repository README files")
        return
    
    # Update manifest
    updated_count = update_manifest_milestones(manifest, all_milestones, args.dry_run)
    
    if not args.dry_run and updated_count > 0:
        if save_manifest(manifest):
            print(f"\n✅ Successfully updated {updated_count} milestones in manifest.json")
        else:
            print("\n❌ Failed to save manifest.json")
    elif args.dry_run:
        print(f"\nDRY RUN: Would update {updated_count} milestones")
    else:
        print("\n✅ No changes needed - all milestones are up to date")

if __name__ == "__main__":
    main()

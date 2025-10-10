#!/usr/bin/env python3
"""
Update all repository README files and automatically commit changes.

This script:
1. Updates README files from manifest.json
2. Automatically commits any changes in each repository
3. Uses consistent commit messages for documentation updates

Usage:
    python3 scripts/update_and_commit_readmes.py [--dry-run] [--repo REPO_NAME]
    
Options:
    --dry-run    Show what would be changed without making changes
    --repo NAME  Only update a specific repository by name
"""

import json
import sys
import argparse
import subprocess
import os
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

def find_description_section(content: str) -> tuple[int, int, str]:
    """
    Find the description section in a README file.
    Returns (start_line, end_line, current_description)
    """
    lines = content.split('\n')
    
    # Look for the pattern: # Title\n\nDescription
    for i, line in enumerate(lines):
        if line.startswith('# ') and i + 2 < len(lines):
            # Check if next line is empty and line after that is the description
            if lines[i + 1].strip() == '' and lines[i + 2].strip():
                # Skip if the next line looks like badges (contains img.shields.io)
                if 'img.shields.io' in lines[i + 2]:
                    continue
                    
                # Find where the description ends (next empty line or next section)
                desc_start = i + 2
                desc_end = desc_start
                
                for j in range(desc_start + 1, len(lines)):
                    if lines[j].strip() == '' or lines[j].startswith('#'):
                        desc_end = j
                        break
                else:
                    desc_end = len(lines)
                
                current_desc = '\n'.join(lines[desc_start:desc_end]).strip()
                return desc_start, desc_end, current_desc
    
    return -1, -1, ""

def update_readme_description(file_path: Path, new_description: str, dry_run: bool = False) -> bool:
    """
    Update the description in a README file.
    Returns True if the file was updated, False if no changes needed.
    """
    if not file_path.exists():
        print(f"WARNING: README not found at {file_path}")
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"ERROR: Failed to read {file_path}: {e}")
        return False
    
    start_line, end_line, current_desc = find_description_section(content)
    
    if start_line == -1:
        print(f"WARNING: Could not find description section in {file_path}")
        return False
    
    # Check if description is already up to date
    if current_desc.strip() == new_description.strip():
        return False
    
    if dry_run:
        print(f"WOULD UPDATE {file_path}:")
        print(f"  Current: {current_desc}")
        print(f"  New:     {new_description}")
        return True
    
    # Update the content
    lines = content.split('\n')
    lines[start_line:end_line] = [new_description]
    new_content = '\n'.join(lines)
    
    try:
        file_path.write_text(new_content, encoding='utf-8')
        print(f"✅ Updated {file_path}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to write {file_path}: {e}")
        return False

def run_git_command(repo_path: Path, command: List[str], dry_run: bool = False) -> Tuple[bool, str]:
    """
    Run a git command in the specified repository.
    Returns (success, output)
    """
    if dry_run:
        print(f"WOULD RUN: git {' '.join(command)} in {repo_path}")
        return True, "dry-run"
    
    try:
        # Set environment to skip pre-commit hooks to prevent recursive execution
        env = os.environ.copy()
        env['SKIP'] = 'pre-commit'
        
        result = subprocess.run(
            ['git'] + command,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
            env=env
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def commit_repo_changes(repo_path: Path, repo_name: str, dry_run: bool = False) -> bool:
    """
    Commit any changes in the repository.
    Returns True if changes were committed, False if no changes.
    """
    # Check if there are any changes
    success, output = run_git_command(repo_path, ['status', '--porcelain'], dry_run)
    if not success:
        print(f"ERROR: Failed to check git status in {repo_path}: {output}")
        return False
    
    if not output.strip():
        return False  # No changes
    
    # Add all changes
    success, output = run_git_command(repo_path, ['add', '.'], dry_run)
    if not success:
        print(f"ERROR: Failed to add changes in {repo_path}: {output}")
        return False
    
    # Commit with appropriate message
    commit_message = f"docs: update README to reflect current project status and progress"
    
    success, output = run_git_command(repo_path, ['commit', '-m', commit_message], dry_run)
    if not success:
        print(f"ERROR: Failed to commit changes in {repo_path}: {output}")
        return False
    
    if not dry_run:
        print(f"✅ Committed changes in {repo_name}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Update repository READMEs and commit changes')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without making changes')
    parser.add_argument('--repo', type=str, 
                       help='Only update a specific repository by name')
    
    args = parser.parse_args()
    
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
    committed_count = 0
    total_count = len(repositories)
    
    print(f"{'DRY RUN: ' if args.dry_run else ''}Updating READMEs and committing changes for {total_count} repositories...")
    print()
    
    for repo in repositories:
        repo_name = repo.get('name')
        short_desc = repo.get('short_description', '')
        
        if not repo_name:
            print(f"WARNING: Repository missing name, skipping")
            continue
            
        if not short_desc:
            print(f"WARNING: Repository '{repo_name}' missing short_description, skipping")
            continue
        
        # Find the README path
        if repo_name not in REPO_PATHS:
            print(f"WARNING: No path mapping for repository '{repo_name}', skipping")
            continue
        
        repo_path = Path(REPO_PATHS[repo_name])
        readme_path = repo_path / "README.md"
        
        if not readme_path.exists():
            print(f"WARNING: README not found for '{repo_name}' at {readme_path}")
            continue
        
        # Update the README
        was_updated = update_readme_description(readme_path, short_desc, args.dry_run)
        if was_updated:
            updated_count += 1
        
        # Commit changes in this repository
        was_committed = commit_repo_changes(repo_path, repo_name, args.dry_run)
        if was_committed:
            committed_count += 1
    
    print()
    if args.dry_run:
        print(f"DRY RUN COMPLETE: Would update {updated_count}/{total_count} repositories")
        print(f"DRY RUN COMPLETE: Would commit changes in {committed_count}/{total_count} repositories")
    else:
        print(f"✅ COMPLETE: Updated {updated_count}/{total_count} repositories")
        print(f"✅ COMPLETE: Committed changes in {committed_count}/{total_count} repositories")
    
    if updated_count == 0 and not args.dry_run:
        print("All READMEs are already up to date!")

if __name__ == "__main__":
    main()

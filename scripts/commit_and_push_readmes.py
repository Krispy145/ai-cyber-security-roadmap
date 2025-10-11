#!/usr/bin/env python3
"""
Script to commit and push updated READMEs from all repositories.
This script is designed to be run after successful pre-commit hooks
that update READMEs across the workspace.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Repository paths relative to the ai-cyber-security-roadmap directory
REPO_PATHS = {
    "ml-foundations": "../ml-foundations",
    "phishing-classifier": "../phishing-classifier", 
    "secure-ai-api": "../secure-ai-api",
    "flutter-ai-chat-rag": "../flutter-ai-chat-rag",
    "flutter-iam-package": "../flutter-iam-package",
    "flutter-api-showcase": "../flutter-api-showcase",
    "react-phishing-dashboard": "../react-phishing-dashboard",
    "react-native-chat-rag": "../react-native-chat-rag",
    "react-native-api-showcase": "../react-native-api-showcase",
    "react-native-iam-package": "../react-native-iam-package",
    "ai-cyber-security-roadmap": "."  # This repo itself
}

def run_command(cmd: List[str], cwd: str = None, capture_output: bool = True) -> Tuple[bool, str, str]:
    """Run a command and return success status, stdout, and stderr."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=False
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_git_status(repo_path: str) -> Tuple[bool, List[str]]:
    """Check if there are any changes in the repository."""
    success, stdout, stderr = run_command(["git", "status", "--porcelain"], cwd=repo_path)
    if not success:
        return False, []
    
    # Parse the output to get changed files
    changed_files = []
    for line in stdout.strip().split('\n'):
        if line.strip():
            # git status --porcelain format: XY filename
            # X = status of index, Y = status of working tree
            # Format can be " M README.md" or "M README.md"
            parts = line.split(None, 1)  # Split on whitespace, max 1 split
            if len(parts) == 2:
                status = parts[0]
                filename = parts[1]
                changed_files.append((status, filename))
    
    return True, changed_files

def commit_and_push_repo(repo_name: str, repo_path: str, dry_run: bool = False) -> bool:
    """Commit and push changes for a single repository."""
    print(f"\n🔄 Processing {repo_name}...")
    
    # Check if directory exists
    if not os.path.exists(repo_path):
        print(f"⚠️  Repository {repo_name} not found at {repo_path}")
        return False
    
    # Check git status
    success, changed_files = check_git_status(repo_path)
    if not success:
        print(f"❌ Failed to check git status for {repo_name}")
        return False
    
    if not changed_files:
        print(f"✅ No changes in {repo_name}")
        return True
    
    # Filter for README changes
    readme_changes = [f for status, f in changed_files if 'README.md' in f]
    other_changes = [f for status, f in changed_files if 'README.md' not in f]
    
    if not readme_changes:
        print(f"ℹ️  No README changes in {repo_name}")
        return True
    
    print(f"📝 README changes detected: {readme_changes}")
    if other_changes:
        print(f"📄 Other changes: {other_changes}")
    
    if dry_run:
        print(f"🔍 DRY RUN: Would commit and push {len(readme_changes)} README changes")
        return True
    
    # Add README files
    for filename in readme_changes:
        success, stdout, stderr = run_command(["git", "add", filename], cwd=repo_path)
        if not success:
            print(f"❌ Failed to add {filename}: {stderr}")
            return False
    
    # Commit changes
    commit_message = f"docs: Update README from ai-cyber-security-roadmap sync\n\nAuto-generated commit from workspace synchronization"
    success, stdout, stderr = run_command(
        ["git", "commit", "-m", commit_message], 
        cwd=repo_path
    )
    
    if not success:
        print(f"❌ Failed to commit in {repo_name}: {stderr}")
        return False
    
    print(f"✅ Committed README changes in {repo_name}")
    
    # Push changes
    success, stdout, stderr = run_command(["git", "push", "origin", "main"], cwd=repo_path)
    if not success:
        # Try other common branch names
        for branch in ["master", "develop"]:
            success, stdout, stderr = run_command(["git", "push", "origin", branch], cwd=repo_path)
            if success:
                break
        
        if not success:
            print(f"❌ Failed to push {repo_name}: {stderr}")
            return False
    
    print(f"✅ Pushed changes for {repo_name}")
    return True

def main():
    """Main function to commit and push README changes across all repositories."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Commit and push updated READMEs from all repositories')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--repo', type=str, help='Only process a specific repository')
    parser.add_argument('--exclude-main', action='store_true', help='Exclude the main ai-cyber-security-roadmap repo')
    args = parser.parse_args()
    
    # Get the script directory (ai-cyber-security-roadmap)
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    print("🚀 Starting README commit and push process...")
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    
    # Filter repositories
    repos_to_process = REPO_PATHS.copy()
    
    if args.repo:
        if args.repo not in repos_to_process:
            print(f"❌ Repository '{args.repo}' not found in known repositories")
            print(f"Available repositories: {list(repos_to_process.keys())}")
            sys.exit(1)
        repos_to_process = {args.repo: repos_to_process[args.repo]}
    
    if args.exclude_main:
        repos_to_process.pop("ai-cyber-security-roadmap", None)
    
    print(f"📋 Processing {len(repos_to_process)} repositories...")
    
    # Process each repository
    success_count = 0
    total_count = len(repos_to_process)
    
    for repo_name, repo_path in repos_to_process.items():
        try:
            if commit_and_push_repo(repo_name, repo_path, args.dry_run):
                success_count += 1
            else:
                print(f"❌ Failed to process {repo_name}")
        except Exception as e:
            print(f"❌ Error processing {repo_name}: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    if args.dry_run:
        print(f"🔍 DRY RUN COMPLETE: Would process {success_count}/{total_count} repositories")
    else:
        print(f"✅ COMPLETE: Successfully processed {success_count}/{total_count} repositories")
    
    if success_count < total_count:
        print(f"⚠️  {total_count - success_count} repositories had issues")
        sys.exit(1)
    else:
        print("🎉 All repositories processed successfully!")

if __name__ == "__main__":
    main()

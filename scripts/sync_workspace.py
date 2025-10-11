#!/usr/bin/env python3
"""
Complete workspace synchronization script.

This script:
1. Validates the manifest.json file
2. Updates all README files to match the standardized template
3. Syncs milestones between repositories and manifest
4. Generates cover images for repositories
5. Sets up pre-commit hooks for consistent development workflow
6. Commits all changes with appropriate messages

Usage:
    python3 scripts/sync_workspace.py [--dry-run] [--skip-hooks] [--repo REPO_NAME]
    
Options:
    --dry-run     Show what would be done without making changes
    --skip-hooks  Skip setting up pre-commit hooks
    --repo NAME   Only sync a specific repository by name
"""

import json
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

def run_script(script_name: str, args: List[str] = None, dry_run: bool = False) -> bool:
    """Run a script from the scripts directory."""
    if args is None:
        args = []
    
    script_path = Path("scripts") / script_name
    if not script_path.exists():
        print(f"ERROR: Script not found: {script_path}")
        return False
    
    command = ["python3", str(script_path)] + args
    
    if dry_run:
        print(f"WOULD RUN: {' '.join(command)}")
        return True
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {script_name} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {script_name} failed")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Complete workspace synchronization')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be done without making changes')
    parser.add_argument('--skip-hooks', action='store_true',
                       help='Skip setting up pre-commit hooks')
    parser.add_argument('--repo', type=str, 
                       help='Only sync a specific repository by name')
    
    args = parser.parse_args()
    
    print(f"{'DRY RUN: ' if args.dry_run else ''}Starting complete workspace synchronization...")
    print("=" * 60)
    
    # Step 1: Validate manifest
    print("\n1. Validating manifest.json...")
    if not run_script("validate_manifest.py", dry_run=args.dry_run):
        print("ERROR: Manifest validation failed")
        sys.exit(1)
    
    # Step 2: Standardize README files
    print("\n2. Standardizing README files...")
    readme_args = ["--repo", args.repo] if args.repo else []
    if not run_script("standardize_readmes.py", readme_args, dry_run=args.dry_run):
        print("ERROR: README standardization failed")
        sys.exit(1)
    
    # Step 3: Sync milestones from README files to manifest
    print("\n3. Syncing milestones to manifest...")
    sync_args = ["--repo", args.repo] if args.repo else []
    if not run_script("sync_roadmaps_to_manifest.py", sync_args, dry_run=args.dry_run):
        print("ERROR: Milestone sync failed")
        sys.exit(1)
    
    # Step 4: Update main README from manifest
    print("\n4. Updating main README from manifest...")
    if not run_script("manifest2readme.py", dry_run=args.dry_run):
        print("ERROR: Main README update failed")
        sys.exit(1)
    
    # Step 5: Generate cover images
    print("\n5. Generating cover images...")
    if not run_script("generate_repo_covers.py", dry_run=args.dry_run):
        print("ERROR: Cover image generation failed")
        sys.exit(1)
    
    # Step 6: Add cover URLs to manifest
    print("\n6. Adding cover URLs to manifest...")
    if not run_script("add_cover_urls.py", dry_run=args.dry_run):
        print("ERROR: Adding cover URLs failed")
        sys.exit(1)
    
    # Step 7: Set up pre-commit hooks (optional)
    if not args.skip_hooks:
        print("\n7. Setting up pre-commit hooks...")
        hook_args = ["--repo", args.repo] if args.repo else []
        if not run_script("setup_precommit_hooks.py", hook_args, dry_run=args.dry_run):
            print("WARNING: Pre-commit hook setup failed (continuing...)")
    else:
        print("\n7. Skipping pre-commit hook setup...")
    
    # Step 8: Final validation
    print("\n8. Final validation...")
    if not run_script("validate_manifest.py", dry_run=args.dry_run):
        print("ERROR: Final validation failed")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    if args.dry_run:
        print("DRY RUN COMPLETE: All synchronization steps would be executed")
    else:
        print("✅ WORKSPACE SYNCHRONIZATION COMPLETE!")
        print("\nNext steps:")
        print("1. Review the changes made to all repositories")
        print("2. Commit and push changes to each repository")
        print("3. Verify that pre-commit hooks are working correctly")
        print("4. Test the synchronization workflow")

if __name__ == "__main__":
    main()

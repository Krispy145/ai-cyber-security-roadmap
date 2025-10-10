#!/usr/bin/env python3
"""
Clean up duplicate milestones in manifest.json.

This script:
1. Identifies duplicate milestones based on title and repo
2. Merges duplicate information (keeps the most complete data)
3. Removes true duplicates
4. Preserves unique milestones

Usage:
    python3 scripts/cleanup_duplicate_milestones.py [--dry-run]
    
Options:
    --dry-run    Show what would be changed without making changes
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Set

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

def cleanup_duplicates(milestones: List[Dict], dry_run: bool = False) -> List[Dict]:
    """
    Clean up duplicate milestones.
    Returns cleaned list of milestones.
    """
    # Group milestones by repo and similar titles
    grouped = {}
    duplicates_found = []
    
    for milestone in milestones:
        repo = milestone.get('repo', '')
        title = milestone.get('title', '')
        
        # Create a normalized key for similar titles
        normalized_title = title.lower().replace(' ', '').replace('-', '').replace('_', '')
        
        # Check for common duplicate patterns
        if 'scaffold' in normalized_title and 'repo' in normalized_title:
            key = f"{repo}:scaffold"
        elif 'secure' in normalized_title and 'api' in normalized_title and 'integration' in normalized_title:
            key = f"{repo}:secure_api_integration"
        elif 'docker' in normalized_title and 'ci' in normalized_title:
            key = f"{repo}:docker_cicd"
        elif 'jwt' in normalized_title and 'auth' in normalized_title:
            key = f"{repo}:jwt_auth"
        else:
            key = f"{repo}:{title}"
        
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(milestone)
    
    # Process each group
    cleaned_milestones = []
    removed_count = 0
    
    for key, milestone_group in grouped.items():
        if len(milestone_group) == 1:
            # No duplicates, keep as is
            cleaned_milestones.append(milestone_group[0])
        else:
            # Found duplicates, merge them
            print(f"Found {len(milestone_group)} duplicates for: {key}")
            duplicates_found.append(key)
            
            # Merge duplicates by keeping the most complete one
            merged = milestone_group[0].copy()
            
            for duplicate in milestone_group[1:]:
                # Merge fields, preferring non-empty values
                for field in ['category', 'status', 'due', 'date', 'id']:
                    if field in duplicate and duplicate[field] and (not merged.get(field) or merged[field] == 'todo'):
                        merged[field] = duplicate[field]
                        print(f"  Updated {field}: {merged.get(field)}")
            
            cleaned_milestones.append(merged)
            removed_count += len(milestone_group) - 1
            
            if dry_run:
                print(f"  WOULD MERGE {len(milestone_group)} duplicates into 1")
            else:
                print(f"  ✅ Merged {len(milestone_group)} duplicates into 1")
    
    if duplicates_found:
        print(f"\nFound duplicates for: {', '.join(duplicates_found)}")
        if dry_run:
            print(f"WOULD REMOVE {removed_count} duplicate milestones")
        else:
            print(f"✅ Removed {removed_count} duplicate milestones")
    else:
        print("✅ No duplicates found")
    
    return cleaned_milestones

def main():
    parser = argparse.ArgumentParser(description='Clean up duplicate milestones in manifest')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without making changes')
    
    args = parser.parse_args()
    
    # Load manifest
    manifest = load_manifest()
    milestones = manifest.get('milestones', [])
    
    print(f"Found {len(milestones)} total milestones")
    
    # Clean up duplicates
    cleaned_milestones = cleanup_duplicates(milestones, args.dry_run)
    
    print(f"After cleanup: {len(cleaned_milestones)} milestones")
    
    if not args.dry_run and len(cleaned_milestones) < len(milestones):
        # Update manifest
        manifest['milestones'] = cleaned_milestones
        
        if save_manifest(manifest):
            print(f"\n✅ Successfully cleaned up manifest.json")
        else:
            print(f"\n❌ Failed to save manifest.json")
    elif args.dry_run:
        print(f"\nDRY RUN: Would clean up {len(milestones) - len(cleaned_milestones)} duplicate milestones")
    else:
        print(f"\n✅ No changes needed")

if __name__ == "__main__":
    main()

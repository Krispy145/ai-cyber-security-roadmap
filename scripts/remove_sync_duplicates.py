#!/usr/bin/env python3
"""
Remove duplicate milestones that were added by the sync script.

This script removes milestones with IDs that follow the pattern:
- {repo}-{number} (e.g., phishing-21, secure-25, ai-32, etc.)

These are the duplicates that were added by the sync script.
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict

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

def main():
    # Load manifest
    manifest = load_manifest()
    milestones = manifest.get('milestones', [])
    
    print(f"Found {len(milestones)} total milestones")
    
    # Remove milestones with sync-generated IDs (pattern: {repo}-{number})
    original_milestones = []
    removed_milestones = []
    
    for milestone in milestones:
        milestone_id = milestone.get('id', '')
        
        # Check if this is a sync-generated ID (e.g., phishing-21, secure-25, etc.)
        # Only match IDs that end with a number >= 20 (the sync script started adding from 21)
        if re.match(r'^[a-z]+-\d+$', milestone_id) and int(milestone_id.split('-')[1]) >= 20:
            removed_milestones.append(milestone)
            print(f"Removing duplicate: {milestone_id} - {milestone.get('title', '')}")
        else:
            original_milestones.append(milestone)
    
    print(f"\nRemoved {len(removed_milestones)} duplicate milestones")
    print(f"Kept {len(original_milestones)} original milestones")
    
    # Update manifest
    manifest['milestones'] = original_milestones
    
    if save_manifest(manifest):
        print(f"\n✅ Successfully cleaned up manifest.json")
    else:
        print(f"\n❌ Failed to save manifest.json")

if __name__ == "__main__":
    main()

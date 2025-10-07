#!/usr/bin/env python3
"""
Add cover image URLs to manifest.json for repositories that have generated covers.
"""

import json
from pathlib import Path

def add_cover_urls_to_manifest(manifest_path="manifest.json"):
    """Add cover URLs to manifest.json for repositories with generated covers."""
    
    # Load manifest
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    # Check each repository for cover images
    for repo in manifest.get("repositories", []):
        repo_name = repo.get("name")
        if not repo_name:
            continue
            
        # Check for cover and thumbnail images
        cover_path = f"images/{repo_name}/{repo_name}-cover.webp"
        thumb_path = f"images/{repo_name}/{repo_name}-thumb.webp"
        
        # Add URLs if images exist
        if Path(cover_path).exists():
            repo["cover_url"] = cover_path
        if Path(thumb_path).exists():
            repo["thumbnail_url"] = thumb_path
    
    # Save updated manifest
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Added cover URLs to manifest.json")
    
    # Show what was added
    for repo in manifest.get("repositories", []):
        repo_name = repo.get("name")
        if repo.get("cover_url") or repo.get("thumbnail_url"):
            print(f"  📸 {repo_name}:")
            if repo.get("cover_url"):
                print(f"    Cover: {repo['cover_url']}")
            if repo.get("thumbnail_url"):
                print(f"    Thumbnail: {repo['thumbnail_url']}")

if __name__ == "__main__":
    add_cover_urls_to_manifest()

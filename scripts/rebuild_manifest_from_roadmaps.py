#!/usr/bin/env python3
"""
Rebuild manifest.json from all repository README roadmaps with proper identifiers.

This script:
1. Scans all repository README files for roadmap tables
2. Extracts milestone information (title, category, target date, status)
3. Assigns proper identifiers using {repo-name}-{number} format
4. Rebuilds the manifest.json milestones section
5. Preserves other manifest data (repositories, progress, etc.)

Usage:
    python3 scripts/rebuild_manifest_from_roadmaps.py [--dry-run]
    
Options:
    --dry-run    Show what would be changed without making changes
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
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a table header row
        if '|' in line and ('Milestone' in line or 'Category' in line):
            in_table = True
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

def generate_identifier(repo_name: str, index: int) -> str:
    """Generate proper identifier using {repo-name}-{number} format."""
    # Convert repo name to identifier format
    if repo_name == "ai-cyber-security-roadmap":
        return f"ai-cyber-{index:02d}"
    elif repo_name == "ml-foundations":
        return f"ml-{index:02d}"
    elif repo_name == "phishing-classifier":
        return f"phishing-{index:02d}"
    elif repo_name == "secure-ai-api":
        return f"secure-ai-api-{index:02d}"
    elif repo_name == "ai-chat-rag":
        return f"ai-chat-{index:02d}"
    elif repo_name == "flutter-iam":
        return f"iam-{index:02d}"
    elif repo_name == "api-showcase":
        return f"api-showcase-{index:02d}"
    else:
        # Fallback: use repo name as-is
        return f"{repo_name}-{index:02d}"

def rebuild_manifest_milestones(manifest: Dict, dry_run: bool = False) -> int:
    """
    Rebuild manifest milestones from all README roadmaps.
    Returns number of milestones processed.
    """
    all_milestones = []
    
    # Extract milestones from all repositories
    for repo_name, repo_path in REPO_PATHS.items():
        milestones = extract_milestones_from_readme(Path(repo_path), repo_name)
        all_milestones.extend(milestones)
        print(f"Found {len(milestones)} milestones in {repo_name}")
    
    if not all_milestones:
        print("No milestones found in any repository README files")
        return 0
    
    # Generate proper identifiers and rebuild milestones
    new_milestones = []
    repo_counters = {}
    seen_milestones = set()  # Track seen milestones to avoid duplicates
    
    for milestone in all_milestones:
        repo = milestone.get('repo', '')
        title = milestone.get('title', '')
        due = milestone.get('due', '')
        
        # Create a unique key for this milestone
        milestone_key = f"{title}|{due}"
        
        # Skip if we've already seen this exact milestone
        if milestone_key in seen_milestones:
            print(f"⚠️  Skipping duplicate: {title} ({repo})")
            continue
        
        seen_milestones.add(milestone_key)
        
        # Initialize counter for this repo
        if repo not in repo_counters:
            repo_counters[repo] = 0
        
        # Increment counter and generate ID
        repo_counters[repo] += 1
        milestone_id = generate_identifier(repo, repo_counters[repo])
        
        # Create new milestone with proper structure
        new_milestone = {
            "id": milestone_id,
            "title": title,
            "category": milestone.get('category', ''),
            "status": milestone.get('status', 'todo'),
            "due": due,
            "repo": repo
        }
        
        # Add date if status is done
        if milestone.get('status') == 'done':
            new_milestone['date'] = due
        
        new_milestones.append(new_milestone)
        
        if dry_run:
            print(f"WOULD ADD {milestone_id}: {title} ({repo})")
        else:
            print(f"✅ Added {milestone_id}: {title} ({repo})")
    
    # Update manifest
    if not dry_run:
        manifest['milestones'] = new_milestones
    
    return len(new_milestones)

def main():
    parser = argparse.ArgumentParser(description='Rebuild manifest from README roadmaps with proper identifiers')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without making changes')
    
    args = parser.parse_args()
    
    # Load manifest
    manifest = load_manifest()
    
    print("Rebuilding manifest milestones from README roadmaps...")
    
    # Rebuild milestones
    milestone_count = rebuild_manifest_milestones(manifest, args.dry_run)
    
    if not args.dry_run and milestone_count > 0:
        if save_manifest(manifest):
            print(f"\n✅ Successfully rebuilt manifest with {milestone_count} milestones")
        else:
            print(f"\n❌ Failed to save manifest.json")
    elif args.dry_run:
        print(f"\nDRY RUN: Would rebuild manifest with {milestone_count} milestones")
    else:
        print(f"\n✅ No changes needed")

if __name__ == "__main__":
    main()

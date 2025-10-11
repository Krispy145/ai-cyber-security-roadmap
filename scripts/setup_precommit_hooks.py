#!/usr/bin/env python3
"""
Set up pre-commit hooks for all repositories in the workspace.

This script:
1. Installs pre-commit in the main roadmap repository
2. Creates appropriate pre-commit configurations for each repository type
3. Installs pre-commit hooks in each repository
4. Ensures consistent development workflow across all repositories

Usage:
    python3 scripts/setup_precommit_hooks.py [--dry-run] [--repo REPO_NAME]
    
Options:
    --dry-run    Show what would be done without making changes
    --repo NAME  Only set up hooks for a specific repository
"""

import json
import sys
import argparse
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional

# Repository name to workspace path mapping
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

def run_command(command: List[str], cwd: Path, dry_run: bool = False) -> bool:
    """Run a command in the specified directory."""
    if dry_run:
        print(f"WOULD RUN: {' '.join(command)} in {cwd}")
        return True
    
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed in {cwd}: {' '.join(command)}")
        print(f"Error: {e.stderr}")
        return False

def get_python_precommit_config() -> str:
    """Get pre-commit configuration for Python repositories."""
    return """repos:
  # Python code formatting and linting
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3
        files: \\.py$
        args: [--line-length=100]

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--profile=black, --line-length=100]

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100, --extend-ignore=E203,W503]

  # General hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-merge-conflict
      - id: check-added-large-files
      - id: check-json
      - id: pretty-format-json
        args: [--autofix, --indent=2]

  # Security checks
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, ., -f, json, -o, bandit-report.json]
        files: \\.py$

  # Type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        files: \\.py$
        args: [--ignore-missing-imports]

  # Markdown formatting
  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.37.0
    hooks:
      - id: markdownlint
        args: [--fix]
"""

def get_flutter_precommit_config() -> str:
    """Get pre-commit configuration for Flutter repositories."""
    return """repos:
  # Dart/Flutter formatting and linting
  - repo: https://github.com/dart-lang/dart_style
    rev: 2.3.2
    hooks:
      - id: dart-format
        files: \.dart$

  - repo: https://github.com/dart-lang/linter
    rev: 1.50.1
    hooks:
      - id: dart-analyze
        files: \.dart$

  # General hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-merge-conflict
      - id: check-added-large-files
      - id: check-json
      - id: pretty-format-json
        args: [--autofix, --indent=2]

  # Markdown formatting
  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.37.0
    hooks:
      - id: markdownlint
        args: [--fix]
"""

def get_react_precommit_config() -> str:
    """Get pre-commit configuration for React repositories."""
    return """repos:
  # JavaScript/TypeScript formatting and linting
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v4.0.0-alpha.8
    hooks:
      - id: prettier
        files: \\.(js|jsx|ts|tsx|json|css|scss|md)$

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.56.0
    hooks:
      - id: eslint
        files: \\.(js|jsx|ts|tsx)$
        additional_dependencies: [eslint@8.56.0, @typescript-eslint/eslint-plugin@6.18.1, @typescript-eslint/parser@6.18.1]

  # General hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-merge-conflict
      - id: check-added-large-files
      - id: check-json
      - id: pretty-format-json
        args: [--autofix, --indent=2]

  # Markdown formatting
  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.37.0
    hooks:
      - id: markdownlint
        args: [--fix]
"""

def get_react_native_precommit_config() -> str:
    """Get pre-commit configuration for React Native repositories."""
    return """repos:
  # JavaScript/TypeScript formatting and linting
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v4.0.0-alpha.8
    hooks:
      - id: prettier
        files: \\.(js|jsx|ts|tsx|json|css|scss|md)$

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.56.0
    hooks:
      - id: eslint
        files: \\.(js|jsx|ts|tsx)$
        additional_dependencies: [eslint@8.56.0, @typescript-eslint/eslint-plugin@6.18.1, @typescript-eslint/parser@6.18.1]

  # General hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-merge-conflict
      - id: check-added-large-files
      - id: check-json
      - id: pretty-format-json
        args: [--autofix, --indent=2]

  # Markdown formatting
  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.37.0
    hooks:
      - id: markdownlint
        args: [--fix]
"""

def get_precommit_config_for_repo(repo_name: str) -> str:
    """Get appropriate pre-commit configuration for a repository."""
    if "flutter" in repo_name:
        return get_flutter_precommit_config()
    elif "react" in repo_name:
        if "native" in repo_name:
            return get_react_native_precommit_config()
        else:
            return get_react_precommit_config()
    elif any(x in repo_name for x in ["ml-foundations", "phishing-classifier", "secure-ai-api"]):
        return get_python_precommit_config()
    else:
        # Default to Python config
        return get_python_precommit_config()

def setup_repo_precommit(repo_name: str, repo_path: Path, dry_run: bool = False) -> bool:
    """Set up pre-commit hooks for a specific repository."""
    if not repo_path.exists():
        print(f"WARNING: Repository path not found: {repo_path}")
        return False
    
    # Check if it's a git repository
    if not (repo_path / ".git").exists():
        print(f"WARNING: {repo_path} is not a git repository, skipping")
        return False
    
    # Create pre-commit configuration
    config_content = get_precommit_config_for_repo(repo_name)
    config_path = repo_path / ".pre-commit-config.yaml"
    
    if dry_run:
        print(f"WOULD CREATE {config_path}")
        print(f"WOULD INSTALL pre-commit hooks in {repo_path}")
        return True
    
    try:
        config_path.write_text(config_content, encoding='utf-8')
        print(f"✅ Created pre-commit config for {repo_name}")
    except Exception as e:
        print(f"ERROR: Failed to create pre-commit config for {repo_name}: {e}")
        return False
    
    # Install pre-commit hooks
    if not run_command(["pre-commit", "install"], repo_path, dry_run):
        print(f"ERROR: Failed to install pre-commit hooks for {repo_name}")
        return False
    
    print(f"✅ Installed pre-commit hooks for {repo_name}")
    return True

def install_precommit_main_repo(dry_run: bool = False) -> bool:
    """Install pre-commit in the main roadmap repository."""
    if dry_run:
        print("WOULD INSTALL pre-commit in main repository")
        return True
    
    # Install pre-commit if not already installed
    try:
        result = subprocess.run(
            ["python3", "-m", "pip", "install", "pre-commit"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Installed pre-commit")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install pre-commit: {e}")
        return False
    
    # Install pre-commit hooks
    if not run_command(["pre-commit", "install"], Path("."), dry_run):
        print("ERROR: Failed to install pre-commit hooks in main repository")
        return False
    
    print("✅ Installed pre-commit hooks in main repository")
    return True

def main():
    parser = argparse.ArgumentParser(description='Set up pre-commit hooks for all repositories')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be done without making changes')
    parser.add_argument('--repo', type=str, 
                       help='Only set up hooks for a specific repository')
    
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
    
    # Install pre-commit in main repository
    if not install_precommit_main_repo(args.dry_run):
        print("ERROR: Failed to set up pre-commit in main repository")
        sys.exit(1)
    
    # Set up pre-commit for each repository
    setup_count = 0
    total_count = len(repositories)
    
    print(f"{'DRY RUN: ' if args.dry_run else ''}Setting up pre-commit hooks for {total_count} repositories...")
    print()
    
    for repo in repositories:
        repo_name = repo.get('name')
        if not repo_name:
            print(f"WARNING: Repository missing name, skipping")
            continue
        
        if repo_name not in REPO_PATHS:
            print(f"WARNING: No path mapping for repository '{repo_name}', skipping")
            continue
        
        repo_path = Path(REPO_PATHS[repo_name])
        
        if setup_repo_precommit(repo_name, repo_path, args.dry_run):
            setup_count += 1
    
    print()
    if args.dry_run:
        print(f"DRY RUN COMPLETE: Would set up pre-commit hooks for {setup_count}/{total_count} repositories")
    else:
        print(f"✅ COMPLETE: Set up pre-commit hooks for {setup_count}/{total_count} repositories")

if __name__ == "__main__":
    main()

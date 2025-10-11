# AI + Cybersecurity Roadmap - Development Makefile

.PHONY: help validate sync readmes covers hooks clean test

# Default target
help:
	@echo "AI + Cybersecurity Roadmap - Available Commands:"
	@echo ""
	@echo "  validate     - Validate manifest.json structure"
	@echo "  sync         - Complete workspace synchronization"
	@echo "  readmes      - Standardize all README files"
	@echo "  covers       - Generate cover images for repositories"
	@echo "  github-sync  - Sync repository descriptions and topics to GitHub"
	@echo "  hooks        - Set up pre-commit hooks for all repositories"
	@echo "  clean        - Clean up generated files"
	@echo "  test         - Run all validation and tests"
	@echo ""
	@echo "  sync-dry     - Dry run of complete synchronization"
	@echo "  readmes-dry  - Dry run of README standardization"
	@echo "  hooks-dry    - Dry run of pre-commit hook setup"
	@echo ""

# Validation
validate:
	@echo "Validating manifest.json..."
	@python3 scripts/validate_manifest.py

# Complete synchronization
sync:
	@echo "Starting complete workspace synchronization..."
	@python3 scripts/sync_workspace.py

sync-dry:
	@echo "Dry run of complete workspace synchronization..."
	@python3 scripts/sync_workspace.py --dry-run

# README management
readmes:
	@echo "Standardizing all README files..."
	@python3 scripts/standardize_readmes.py

readmes-dry:
	@echo "Dry run of README standardization..."
	@python3 scripts/standardize_readmes.py --dry-run

# Cover image generation
covers:
	@echo "Generating cover images..."
	@python3 scripts/generate_repo_covers.py
	@python3 scripts/add_cover_urls.py

# GitHub repository sync
github-sync:
	@echo "Syncing repository descriptions and topics to GitHub..."
	@python3 scripts/sync_github_repos.py

github-sync-dry:
	@echo "Dry run of GitHub repository sync..."
	@python3 scripts/sync_github_repos.py --dry-run

# Pre-commit hooks
hooks:
	@echo "Setting up pre-commit hooks..."
	@python3 scripts/setup_precommit_hooks.py

hooks-dry:
	@echo "Dry run of pre-commit hook setup..."
	@python3 scripts/setup_precommit_hooks.py --dry-run

# Clean up
clean:
	@echo "Cleaning up generated files..."
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "bandit-report.json" -delete
	@find . -name ".coverage" -delete
	@find . -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null || true

# Testing
test: validate
	@echo "Running all tests..."
	@python3 scripts/validate_manifest.py
	@echo "All tests passed!"

# Individual repository operations
sync-repo:
	@if [ -z "$(REPO)" ]; then \
		echo "Usage: make sync-repo REPO=repository-name"; \
		exit 1; \
	fi
	@echo "Syncing repository: $(REPO)"
	@python3 scripts/sync_workspace.py --repo $(REPO)

readmes-repo:
	@if [ -z "$(REPO)" ]; then \
		echo "Usage: make readmes-repo REPO=repository-name"; \
		exit 1; \
	fi
	@echo "Standardizing README for repository: $(REPO)"
	@python3 scripts/standardize_readmes.py --repo $(REPO)

# Development workflow
dev-setup: hooks
	@echo "Development setup complete!"
	@echo "Pre-commit hooks are now active."

dev-sync: sync
	@echo "Workspace synchronized!"
	@echo "All repositories are now up to date."

# Quick commands
quick-sync: readmes sync
	@echo "Quick synchronization complete!"

# Help for specific targets
help-sync:
	@echo "Sync Commands:"
	@echo "  sync         - Complete workspace synchronization"
	@echo "  sync-dry     - Dry run of synchronization"
	@echo "  sync-repo    - Sync specific repository (use REPO=name)"
	@echo "  quick-sync   - Quick sync (readmes + milestones)"

help-readmes:
	@echo "README Commands:"
	@echo "  readmes      - Standardize all README files"
	@echo "  readmes-dry  - Dry run of README standardization"
	@echo "  readmes-repo - Standardize specific repository (use REPO=name)"

help-hooks:
	@echo "Pre-commit Hook Commands:"
	@echo "  hooks        - Set up pre-commit hooks for all repositories"
	@echo "  hooks-dry    - Dry run of pre-commit hook setup"
	@echo "  dev-setup    - Complete development setup"

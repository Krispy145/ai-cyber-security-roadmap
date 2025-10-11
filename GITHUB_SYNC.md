# GitHub Repository Sync

This document explains how to sync repository descriptions and topics from the manifest.json to GitHub using the GitHub API.

## 🚀 Quick Start

### 1. Create a GitHub Personal Access Token

1. Go to [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a descriptive name like "AI Roadmap Sync"
4. Select the following scopes:
   - `repo` (for private repositories) OR `public_repo` (for public repositories only)
   - `read:org` (if you have organization repositories)
5. Copy the generated token

### 2. Set the Token

**Option A: Environment Variable (Recommended)**

```bash
export GITHUB_TOKEN="your_token_here"
```

**Option B: Command Line**

```bash
python3 scripts/sync_github_repos.py --token "your_token_here"
```

### 3. Run the Sync

**Dry Run (Recommended First)**

```bash
make github-sync-dry
# or
python3 scripts/sync_github_repos.py --dry-run
```

**Actual Sync**

```bash
make github-sync
# or
python3 scripts/sync_github_repos.py
```

## 📋 What Gets Synced

The script syncs the following from `manifest.json` to GitHub:

- **Repository Description** → Uses `short_description` field
- **Repository Topics** → Uses `topics` array field

## 🎯 Examples

### Sync All Repositories

```bash
# Dry run first
python3 scripts/sync_github_repos.py --dry-run

# Then sync for real
python3 scripts/sync_github_repos.py
```

### Sync Specific Repository

```bash
# Dry run
python3 scripts/sync_github_repos.py --dry-run --repo react-phishing-dashboard

# Sync
python3 scripts/sync_github_repos.py --repo react-phishing-dashboard
```

### Using Makefile

```bash
# Dry run
make github-sync-dry

# Sync all
make github-sync
```

## 🔧 Configuration

### Repository Mapping

The script automatically extracts the GitHub owner and repository name from the `url` field in manifest.json:

```json
{
  "name": "react-phishing-dashboard",
  "url": "https://github.com/Krispy145/react-phishing-dashboard",
  "short_description": "React + TS + Vite: auth, protected routes, samples table, predict form (later).",
  "topics": ["react", "typescript", "vite", "axios", "zustand", "jwt"]
}
```

This will update:

- **Description**: "React + TS + Vite: auth, protected routes, samples table, predict form (later)."
- **Topics**: react, typescript, vite, axios, zustand, jwt

## 🛡️ Safety Features

- **Dry Run Mode**: Always test with `--dry-run` first
- **Rate Limiting**: Built-in delays to respect GitHub API limits
- **Error Handling**: Graceful handling of missing repositories or API errors
- **Validation**: Checks if repositories exist before attempting updates

## 📊 Output

The script provides detailed output showing:

- Which repositories are being processed
- What changes would be made (dry run) or were made (actual run)
- Success/failure status for each repository
- Summary of total changes

## 🔄 Integration with Workflow

This script integrates perfectly with the existing workspace sync:

```bash
# Complete workflow including GitHub sync
make sync && make github-sync
```

## 🚨 Troubleshooting

### Common Issues

**1. "Bad credentials" Error**

- Check your GitHub token is valid
- Ensure token has correct scopes (repo or public_repo)

**2. "Repository not found" Error**

- Verify the repository exists on GitHub
- Check the URL in manifest.json is correct

**3. "Rate limit exceeded" Error**

- Wait a few minutes and try again
- The script includes built-in rate limiting

### Debug Mode

For more detailed output, you can modify the script to add debug logging or run individual repository syncs to isolate issues.

## 📝 Notes

- The script only updates descriptions and topics, not other repository settings
- Changes are made via GitHub REST API v3
- All operations respect GitHub's rate limits
- The script is idempotent - running it multiple times is safe

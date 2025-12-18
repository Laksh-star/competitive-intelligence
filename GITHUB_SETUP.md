# GitHub Setup Guide

This guide shows how to publish your Competitive Intelligence Monitor to GitHub.

## Before You Publish

### ⚠️ Security Check

Make sure these files are in `.gitignore` (already configured):
- ✅ `.env` - Contains your API keys
- ✅ `intelligence_report_*.txt` - May contain sensitive data
- ✅ `*.log` - Log files

### Verify .env is Ignored

```bash
# Check .gitignore
cat .gitignore | grep .env

# Should show:
# .env
# *.env.local
```

## Step 1: Initialize Git Repository

```bash
cd /Users/ln/Downloads/cocoindex

# Initialize git
git init

# Add all files (respects .gitignore)
git add .

# Check what will be committed
git status

# You should NOT see .env or intelligence_report_*.txt in the list
```

## Step 2: First Commit

```bash
# Create initial commit
git commit -m "Initial commit: Competitive Intelligence Monitor

- CocoIndex pipeline for tracking competitors
- Tavily AI search integration
- GPT-4o-mini LLM extraction via OpenRouter
- PostgreSQL dual indexing
- Interactive CLI and reporting tools
- Complete documentation"
```

## Step 3: Create GitHub Repository

### Option A: Using GitHub CLI

```bash
# Install GitHub CLI if needed
# brew install gh  # macOS
# Or download from: https://cli.github.com/

# Login
gh auth login

# Create repository
gh repo create competitive-intelligence --public --source=. --remote=origin --push

# Or for private:
gh repo create competitive-intelligence --private --source=. --remote=origin --push
```

### Option B: Using GitHub Website

1. Go to https://github.com/new
2. Repository name: `competitive-intelligence`
3. Description: "AI-powered competitive intelligence monitor using CocoIndex, Tavily Search, and LLM extraction"
4. Choose Public or Private
5. Don't initialize with README (we have one)
6. Click "Create repository"

Then connect your local repo:

```bash
# Add remote
git remote add origin https://github.com/YOUR-USERNAME/competitive-intelligence.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 4: Verify Upload

Check that your repository:
- ✅ Has all code files
- ✅ Has all documentation (README, guides)
- ✅ Does NOT have .env file
- ✅ Does NOT have intelligence_report_*.txt files
- ✅ README displays nicely with badges

## Step 5: Add Repository Details

On GitHub, add:

**Description**:
```
AI-powered competitive intelligence monitor using CocoIndex, Tavily Search, and LLM extraction
```

**Topics** (click gear icon):
- `competitive-intelligence`
- `cocoindex`
- `ai`
- `llm`
- `data-pipeline`
- `tavily`
- `openrouter`
- `python`
- `postgresql`

**Website**: (optional)
- Link to your deployment or documentation

## Step 6: Enable GitHub Features

### Enable Issues
Settings → Features → ✅ Issues

### Add README Sections
Your README already has:
- ✅ Badges
- ✅ Architecture diagrams
- ✅ Setup instructions
- ✅ Usage examples
- ✅ Contributing guidelines

### Add Branch Protection (Optional)
Settings → Branches → Add rule → `main`
- ✅ Require pull request reviews

## Files That Will Be Published

### Core Files
- ✅ `main.py` - Pipeline definition
- ✅ `pyproject.toml` - Dependencies
- ✅ `.env.example` - Environment template (safe, no secrets)

### Utilities
- ✅ `run_interactive.py` - Interactive CLI
- ✅ `test_results.py` - Testing
- ✅ `generate_report.py` - Reporting
- ✅ `clear_and_run.py` - Testing utility

### Documentation
- ✅ `README.md` - Main documentation
- ✅ `QUICKSTART.md` - Quick setup
- ✅ `USAGE_GUIDE.md` - Complete reference
- ✅ `TESTING.md` - Testing guide
- ✅ `INTERACTIVE_DEMO.md` - Examples
- ✅ `CLAUDE.md` - Developer guide
- ✅ `CONTRIBUTING.md` - Contribution guidelines
- ✅ `LICENSE` - MIT license

### Files EXCLUDED (in .gitignore)
- ❌ `.env` - Your credentials
- ❌ `intelligence_report_*.txt` - Your reports
- ❌ `__pycache__/` - Python cache
- ❌ `.cocoindex/` - CocoIndex cache

## Post-Publication Checklist

- [ ] Repository is public/private as intended
- [ ] README displays correctly
- [ ] Badges show up
- [ ] .env file is NOT visible
- [ ] No API keys in commit history
- [ ] Issues are enabled
- [ ] Topics are added
- [ ] Description is set

## Updating Repository

```bash
# Make changes to files
# ...

# Stage changes
git add .

# Commit
git commit -m "Description of changes"

# Push to GitHub
git push
```

## Common Issues

### "fatal: not a git repository"
**Solution**: Run `git init` first

### ".env file is showing up"
**Solution**:
```bash
# Remove from git (keeps local file)
git rm --cached .env

# Verify .gitignore contains .env
echo ".env" >> .gitignore

# Commit
git commit -m "Remove .env from git"
git push
```

### "Want to change repository name"
**Solution**:
1. Go to repository Settings on GitHub
2. Scroll to "Repository name"
3. Change name
4. Update local remote:
```bash
git remote set-url origin https://github.com/YOUR-USERNAME/NEW-NAME.git
```

## Sample Repository Description

For GitHub repository About section:

```
🔍 Competitive Intelligence Monitor

AI-powered pipeline that automatically tracks competitors across the web,
extracts structured intelligence using LLM analysis, and stores it in
PostgreSQL for querying and reporting.

Built with CocoIndex | Powered by Tavily AI Search | LLM extraction via OpenRouter
```

## README Preview

Your README will show:
- Python 3.11+ badge
- CocoIndex 0.3.9+ badge
- MIT License badge
- Clear architecture diagram
- Step-by-step setup
- Interactive mode demo
- Project structure
- Contributing guidelines

## Next Steps After Publishing

1. **Share**: Tweet about it, post on LinkedIn
2. **Star**: Star the CocoIndex repo to show appreciation
3. **Iterate**: Accept contributions, add features
4. **Document**: Keep README updated with new features
5. **Engage**: Respond to issues and PRs

---

Ready to publish? Run these commands:

```bash
git init
git add .
git commit -m "Initial commit: Competitive Intelligence Monitor"
gh repo create competitive-intelligence --public --source=. --remote=origin --push
```

Or follow Option B above for manual GitHub repository creation.

# GitHub Publishing Checklist

Use this checklist before publishing to ensure everything is ready.

## Pre-Publication Security Check

- [ ] `.env` file is listed in `.gitignore`
- [ ] `intelligence_report_*.txt` files are excluded
- [ ] No API keys in code (all in `.env`)
- [ ] `.env.example` has placeholder values only
- [ ] No sensitive company data in test files

## Files to Publish (18 files)

### Core Application (5 files)
- [ ] `main.py` (13KB) - Pipeline definition
- [ ] `run_interactive.py` (8.4KB) - Interactive CLI
- [ ] `test_results.py` (7.9KB) - Testing suite
- [ ] `generate_report.py` (6.6KB) - Report generator
- [ ] `clear_and_run.py` (2.7KB) - Fresh data utility

### Configuration (3 files)
- [ ] `pyproject.toml` (552B) - Dependencies
- [ ] `.env.example` (521B) - Environment template
- [ ] `.gitignore` (501B) - Git exclusions

### Documentation (9 files)
- [ ] `README.md` (12KB) - Main documentation
- [ ] `TESTING.md` (14KB) - Testing guide
- [ ] `QUICKSTART.md` (4.2KB) - Quick start
- [ ] `USAGE_GUIDE.md` (5.4KB) - Usage reference
- [ ] `GITHUB_SETUP.md` (6.0KB) - Publishing guide
- [ ] `INTERACTIVE_DEMO.md` (5.6KB) - Interactive examples
- [ ] `CLAUDE.md` (4.8KB) - Developer guidance
- [ ] `CONTRIBUTING.md` (3.6KB) - Contribution guidelines
- [ ] `LICENSE` (1.1KB) - MIT license

### Files EXCLUDED (will NOT be published)
- [ ] `.env` - Your credentials (git-ignored)
- [ ] `intelligence_report_*.txt` - Your reports (git-ignored)
- [ ] `__pycache__/` - Python cache (git-ignored)
- [ ] `.cocoindex/` - CocoIndex cache (git-ignored)

## README Quality Check

- [ ] Badges display correctly (Python, CocoIndex, License)
- [ ] Architecture diagram is clear
- [ ] Setup instructions are complete
- [ ] Examples work
- [ ] Links are valid

## Documentation Completeness

- [ ] Installation steps are clear
- [ ] API keys setup explained
- [ ] Usage examples provided
- [ ] Testing procedures documented
- [ ] Contributing guidelines available
- [ ] License specified (MIT)

## Repository Configuration

- [ ] Choose visibility: Public or Private
- [ ] Add repository description
- [ ] Add topics/tags
- [ ] Enable Issues
- [ ] Add .gitignore
- [ ] Add LICENSE

## Git Commands to Run

```bash
# Navigate to project
cd /Users/ln/Downloads/cocoindex

# Initialize git
git init

# Stage all files (respects .gitignore)
git add .

# Verify what will be committed
git status

# Check that .env is NOT in the list
# Check that intelligence_report_*.txt is NOT in the list

# Create initial commit
git commit -m "Initial commit: Competitive Intelligence Monitor

- CocoIndex pipeline for tracking competitors
- Tavily AI search integration
- GPT-4o-mini LLM extraction via OpenRouter
- PostgreSQL dual indexing
- Interactive CLI and reporting tools
- Complete documentation"
```

## GitHub Repository Creation

### Option A: Using GitHub CLI

```bash
# Make sure gh is installed
gh --version

# Create public repository
gh repo create competitive-intelligence --public --source=. --remote=origin --push

# Or create private repository
gh repo create competitive-intelligence --private --source=. --remote=origin --push
```

### Option B: Manual Creation

1. [ ] Go to https://github.com/new
2. [ ] Repository name: `competitive-intelligence`
3. [ ] Description: "AI-powered competitive intelligence monitor using CocoIndex, Tavily Search, and LLM extraction"
4. [ ] Choose Public or Private
5. [ ] Do NOT initialize with README
6. [ ] Click "Create repository"
7. [ ] Follow the "push an existing repository" instructions

```bash
git remote add origin https://github.com/YOUR-USERNAME/competitive-intelligence.git
git branch -M main
git push -u origin main
```

## Post-Publication Tasks

- [ ] Verify repository shows all files correctly
- [ ] Confirm .env is NOT visible
- [ ] Confirm intelligence reports are NOT visible
- [ ] Check README renders properly
- [ ] Test clone and setup on fresh machine (optional)
- [ ] Add repository topics on GitHub
- [ ] Enable Issues in repository settings
- [ ] Star the CocoIndex repository to show appreciation

## Repository Metadata

**Description**:
```
AI-powered competitive intelligence monitor using CocoIndex, Tavily Search, and LLM extraction
```

**Topics** (add on GitHub):
```
competitive-intelligence
cocoindex
ai
llm
data-pipeline
tavily
openrouter
python
postgresql
```

## Verification Commands

```bash
# Check what will be committed
git status

# View .gitignore rules
cat .gitignore

# Verify .env is excluded
git check-ignore .env
# Should output: .env

# Verify reports are excluded
git check-ignore intelligence_report_2025-12-18_18-00-25.txt
# Should output the filename

# Check remote
git remote -v

# View commit history
git log --oneline
```

## Troubleshooting

### If .env appears in git status
```bash
git rm --cached .env
git commit -m "Remove .env from tracking"
```

### If you committed secrets by accident
```bash
# DO NOT PUSH!
git reset --soft HEAD~1
# Add .env to .gitignore
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"
```

### If you pushed secrets
1. Rotate all API keys immediately
2. Use BFG Repo-Cleaner or git-filter-branch
3. Force push after cleaning

## Success Indicators

✅ Repository is live on GitHub
✅ README displays with formatting
✅ Badges show correctly
✅ No sensitive data visible
✅ Issues are enabled
✅ License is displayed
✅ Topics are added
✅ Description is set

## Next Steps After Publishing

1. **Share**: Post on social media, LinkedIn
2. **Iterate**: Accept contributions, add features
3. **Maintain**: Respond to issues and PRs
4. **Update**: Keep documentation current
5. **Engage**: Build community around project

---

**Ready?** Start with the Git Commands section above!

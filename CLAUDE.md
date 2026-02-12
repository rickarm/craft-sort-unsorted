# CLAUDE.md - AI Assistant Guide

This file provides context and guidelines for AI assistants working on this project.

## Project Overview

**Craft Unsorted Document Auto-Sorter** - An automated Python script that processes unsorted documents in Craft (a note-taking app), intelligently tags them based on content patterns, and moves them to appropriate folders.

**Key Purpose:** Save time by automatically organizing hundreds of accumulated documents every Friday morning.

## Architecture

### Core Components

1. **craft_unsorted_sorter.py** - Main automation script
   - Uses Craft Partner API v1
   - Pattern matching for document classification
   - Tag-based categorization system
   - Automated folder filing

2. **Configuration**
   - `.env` - API credentials (NEVER commit this)
   - `TAG_MAPPING` dict - Document type definitions with patterns and destinations

3. **Scheduling**
   - Runs via cron every Friday at 9:00 AM PT
   - Uses Python virtual environment for isolation

### Technology Stack

- **Python 3.6+** with virtual environment
- **Dependencies:** requests, python-dotenv
- **API:** Craft Partner API (https://connect.craft.do/links/7MlUnGdilB0/api/v1)
- **Logging:** File-based to ~/Library/Logs/CraftAutoSort/
- **Scheduling:** macOS cron

## Important Constraints

### Security

⚠️ **CRITICAL:** The `.env` file contains the real API key and must NEVER be committed to git.

- Always use `.env.example` for templates
- Verify `.gitignore` includes `.env` before any git operations
- API key format: `CRAFT_API_KEY=pdk_xxxxx...`
- Use environment variables, never hardcode credentials

### API Limitations

- Base URL: `https://connect.craft.do/links/7MlUnGdilB0/api/v1`
- Authentication: Bearer token in Authorization header
- Rate limits: Unknown, but we process documents sequentially with API calls
- Timeout: 30 seconds per request

### Craft API Endpoints Used

```
GET  /documents?location=unsorted  - List unsorted documents
GET  /blocks?id={docId}             - Get document content
GET  /folders                       - List all folders
POST /blocks                        - Add tags to documents
PUT  /documents/move                - Move documents to folders
```

Response structure uses `items` key (not `documents` or `data`).

### Pattern Matching System

Documents are classified by priority (lower number = higher priority):

1. **person** (priority 1) - REFERENCE/People
2. **company** (priority 2) - REFERENCE/Companies
3. **client-session** (priority 3) - COACHING/Clients
4. **family-email** (priority 4) - PERSONAL/Home/Family Emails
5. **tax** (priority 5) - PERSONAL/Finances/Tax
6. **packing-list** (priority 6) - PERSONAL/Travel/Packing Lists
7. **reference-article** (priority 7) - REFERENCE/Articles
8. **coaching-research** (priority 8) - REFERENCE/Research

Each tag has:
- `destination_folder` - Path like "COACHING/Clients"
- `patterns` - Regex list for matching
- `keywords` - Simple string matching
- `priority` - Lower = checked first

## Development Guidelines

### When Modifying Detection Logic

1. **Test patterns carefully** - Regex patterns use RE2 syntax
2. **Consider priority order** - Earlier patterns take precedence
3. **Check folder paths exist** - Script logs warnings if folders not found
4. **Test on small batch first** - Don't process all 800+ documents immediately

### When Adding New Document Types

```python
"new-tag": {
    "destination_folder": "FOLDER/Subfolder",
    "patterns": [r"regex_pattern1", r"regex_pattern2"],
    "keywords": ["keyword1", "keyword2"],
    "priority": 9,  # Set appropriately
}
```

### When Modifying API Calls

- Always include timeout (30 seconds)
- Wrap in try/except with proper logging
- Check response structure matches Craft API docs
- Use `response.raise_for_status()` for error handling
- Log both request URL and response for debugging

### Error Handling Philosophy

- **Fail gracefully** - Log errors but continue processing other documents
- **Never expose API keys** - Check logging doesn't include headers
- **Provide actionable errors** - Log enough context to debug
- **Track statistics** - Count processed, tagged, moved, errors

## Common Tasks

### Testing the Script

```bash
# Manual test run (processes ALL unsorted docs)
./craft_unsorted_sorter.py

# View logs
tail -f ~/Library/Logs/CraftAutoSort/craft_sort_$(date +%Y%m).log
```

### Modifying Tag Patterns

1. Edit `TAG_MAPPING` in craft_unsorted_sorter.py
2. Test with manual run
3. Check logs to verify correct classification
4. Adjust patterns as needed

### Updating Dependencies

```bash
source venv/bin/activate
pip install <package>
pip freeze > requirements.txt  # If you add this file
```

## File Structure

```
craft-sort-unsorted/
├── .env                      # API key (PROTECTED)
├── .env.example              # Template
├── .gitignore                # Security
├── README.md                 # User documentation
├── QUICKSTART.md             # Quick reference
├── CLAUDE.md                 # This file
├── craft_unsorted_sorter.py  # Main script
├── setup.sh                  # First-time setup
├── setup_cron.sh             # Cron installer
└── venv/                     # Python environment
```

## Folder Mapping

The script expects these folders to exist in Craft:

- `COACHING/Clients`
- `PERSONAL/Home/Family Emails`
- `PERSONAL/Finances/Tax`
- `PERSONAL/Travel/Packing Lists`
- `REFERENCE/Articles`
- `REFERENCE/Research`
- `REFERENCE/People`
- `REFERENCE/Companies`

If folders don't exist, documents are tagged but not moved (logged as warning).

## Git Workflow

### Protected Files (Never Commit)

- `.env` - Real API key
- `venv/` - Virtual environment
- `*.log` - Log files
- `.claude/` - Claude Code metadata

### Safe to Commit

- Code changes to .py files
- Documentation updates
- Pattern/mapping changes
- Setup scripts

### Before Committing

```bash
# Verify .env is excluded
git status --ignored | grep .env

# Check what's staged
git diff --cached

# Commit with co-author
git commit -m "Description

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

## Debugging Tips

### Document Not Being Detected

1. Check the document title and content
2. Test patterns in Python REPL:
   ```python
   import re
   text = "your document title".lower()
   pattern = r"your_regex"
   re.search(pattern, text)
   ```
3. Check priority order - earlier patterns win
4. Enable debug logging for more detail

### API Errors

1. Verify `.env` exists and has valid key
2. Check network connectivity
3. Review API response in logs
4. Confirm endpoint URLs match current API version

### Cron Not Running

1. Check cron job exists: `crontab -l`
2. Check cron logs: `cat cron.log`
3. Verify Python path: `which python3`
4. Test manual run works: `./craft_unsorted_sorter.py`

## Performance Considerations

- **Processing time:** ~2 seconds per document (API calls + pattern matching)
- **800 documents:** ~25-30 minutes total
- **API calls:** 3-4 per document (get content, tag, get folders, move)
- **Logging:** Rotates monthly, one file per month

## Future Improvements (Ideas)

- [ ] Add dry-run mode for testing patterns
- [ ] Parallel processing with rate limiting
- [ ] Machine learning for classification
- [ ] Web dashboard for monitoring
- [ ] Email summary after each run
- [ ] Backup documents before moving
- [ ] Undo functionality
- [ ] Custom rules per folder

## Contact & Support

**Owner:** Richard Armbrust

**Documentation:**
- README.md - Full user guide
- QUICKSTART.md - Quick reference
- This file - Developer guide

**Logs Location:** `~/Library/Logs/CraftAutoSort/`

**Repository:** Local only (not published)

---

*Last Updated: 2026-02-11*
*AI Assistant: Follow these guidelines when making changes to ensure consistency and security.*

# Quick Start Guide

## First Time Setup

```bash
cd /Users/richardarmbrust/Dev/craft-sort-unsorted
./setup.sh
./setup_cron.sh
```

That's it! The script will now run automatically every Friday at 9 AM PT.

## Common Commands

### Manual Run
```bash
./craft_unsorted_sorter.py
```

### View Logs
```bash
# Current month's logs
tail -f ~/Library/Logs/CraftAutoSort/craft_sort_$(date +%Y%m).log

# Cron logs
tail -f cron.log
```

### Check Cron Job
```bash
crontab -l | grep craft
```

### Update API Key
```bash
nano .env
# Change CRAFT_API_KEY value
```

## File Structure

```
craft-sort-unsorted/
├── .env                    # API key (DO NOT COMMIT)
├── .env.example            # Template for .env
├── .gitignore              # Protects .env from git
├── README.md               # Full documentation
├── QUICKSTART.md           # This file
├── craft_unsorted_sorter.py # Main script
├── setup.sh                # First-time setup
├── setup_cron.sh           # Install cron job
└── venv/                   # Python virtual environment
```

## Customization

Edit `TAG_MAPPING` in `craft_unsorted_sorter.py` to:
- Add new document types
- Change destination folders
- Modify detection patterns
- Adjust priority order

## Troubleshooting

### Script not running
```bash
# Check if cron job exists
crontab -l

# Test manually
./craft_unsorted_sorter.py

# Check logs
cat ~/Library/Logs/CraftAutoSort/craft_sort_*.log
```

### API errors
```bash
# Verify .env exists
cat .env

# Check API key format
# Should be: CRAFT_API_KEY=pdk_xxxxx...
```

## Git Commands

```bash
# Check status
git status

# View history
git log --oneline

# See what's ignored
git status --ignored
```

## Schedule

The script runs automatically:
- **When:** Every Friday at 9:00 AM Pacific Time
- **What:** Processes all documents in "Unsorted"
- **How:** Tags and moves to appropriate folders
- **Logs:** ~/Library/Logs/CraftAutoSort/

## Support

For issues or questions, check:
1. README.md for full documentation
2. Logs for detailed error messages
3. .env for API key configuration

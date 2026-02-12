# Craft Unsorted Document Auto-Sorter

Automatically sorts unsorted Craft documents by detecting their type and moving them to appropriate folders.

## Features

- 🔍 **Smart Detection**: Analyzes document titles and content to detect document type
- 🏷️ **Auto-Tagging**: Adds appropriate hashtags to documents
- 📁 **Auto-Filing**: Moves documents to designated folders
- 📊 **Logging**: Comprehensive logging to track all operations
- ⏰ **Scheduled**: Runs automatically every Friday at 9 AM PT

## Setup

### Prerequisites

- Python 3.6 or higher
- Craft API access with a Partner Development Key

### Quick Start

Run the setup script (already configured with your API key):

```bash
cd /Users/richardarmbrust/Dev/craft-sort-unsorted
./setup.sh
```

This will:
- Create a Python virtual environment
- Install all required dependencies (requests, python-dotenv)
- Set up the .env configuration file
- Make all scripts executable

### Manual Setup (Alternative)

If you prefer to set up manually:

1. Create virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install requests python-dotenv
```

2. Configure your Craft API key:

The `.env` file is already created with your API key. If you need to change it:

```bash
nano .env
```

**Important:** Never commit the `.env` file to version control. It's already in `.gitignore`.

3. Make scripts executable:
```bash
chmod +x craft_unsorted_sorter.py setup_cron.sh
```

### Install Scheduled Run

After setup, install the cron job to run automatically every Friday at 9 AM:
```bash
./setup_cron.sh
```

## Usage

### Manual Run

To run the script manually:
```bash
python3 craft_unsorted_sorter.py
```

### Automated Schedule

The script runs automatically every Friday at 9:00 AM Pacific Time via cron.

To verify the cron job is installed:
```bash
crontab -l
```

### Logs

Logs are stored in:
- **Script logs**: `~/Library/Logs/CraftAutoSort/craft_sort_YYYYMM.log`
- **Cron logs**: `/Users/richardarmbrust/Dev/craft-sort-unsorted/cron.log`

View recent logs:
```bash
tail -f ~/Library/Logs/CraftAutoSort/craft_sort_$(date +%Y%m).log
```

## Document Detection Rules

The script uses pattern matching and keywords to classify documents:

| Tag | Destination | Patterns |
|-----|------------|----------|
| `#client-session` | COACHING/Clients | Client names with dates, session notes |
| `#family-email` | PERSONAL/Home/Family Emails | "Week of" patterns |
| `#tax` | PERSONAL/Finances/Tax | Tax-related keywords |
| `#packing-list` | PERSONAL/Travel/Packing Lists | Packing/travel keywords |
| `#reference-article` | REFERENCE/Articles | URLs, article keywords |
| `#coaching-research` | REFERENCE/Research | Coaching/leadership keywords |
| `#person` | REFERENCE/People | Person/bio keywords |
| `#company` | REFERENCE/Companies | Company keywords |
| `#general` | (stays in Unsorted) | Fallback for unmatched documents |

## Customization

Edit `TAG_MAPPING` in `craft_unsorted_sorter.py` to:
- Add new document types
- Modify detection patterns
- Change destination folders
- Adjust priority order

Example:
```python
TAG_MAPPING = {
    "my-custom-tag": {
        "destination_folder": "MY_FOLDER/Subfolder",
        "patterns": [r"pattern1", r"pattern2"],
        "keywords": ["keyword1", "keyword2"],
        "priority": 1,  # Lower = higher priority
    },
}
```

## Troubleshooting

### Script not running automatically
1. Check cron is running: `ps aux | grep cron`
2. Verify cron job: `crontab -l`
3. Check cron logs: `cat /Users/richardarmbrust/Dev/craft-sort-unsorted/cron.log`
4. Ensure Python path is correct: `which python3`

### API errors
1. Verify API key is set in `.env` file
2. Check that `.env` file exists in the script directory
3. Verify API key is valid
4. Check network connectivity
5. Review script logs for detailed error messages
6. Ensure folder paths in `TAG_MAPPING` match your Craft structure

### Documents not being detected
1. Review the detection patterns in `TAG_MAPPING`
2. Check if document content is accessible
3. Run the script manually with debug logging
4. Verify folder paths exist in your Craft workspace

### Remove cron job
```bash
crontab -l | grep -vF 'craft_unsorted_sorter.py' | crontab -
```

## Architecture

```
craft_unsorted_sorter.py
├── Environment Loading (.env)
├── Configuration (TAG_MAPPING)
├── API Helpers
│   ├── get_unsorted_documents()
│   ├── get_document_content()
│   ├── get_folder_by_path()
│   ├── add_tag_to_document()
│   └── move_document()
├── Detection Logic
│   └── detect_tag()
└── Main Automation
    └── run_automation()

Configuration Files:
├── .env (API keys - not in git)
├── .env.example (template)
└── .gitignore (protects secrets)
```

## API Endpoints Used

- `GET /documents?location=unsorted` - List unsorted documents
- `GET /blocks?id={docId}` - Get document content
- `GET /folders` - List all folders
- `POST /blocks` - Add tags to documents
- `PUT /documents/move` - Move documents to folders

## Security

### API Key Storage

Your Craft API key is stored in the `.env` file, which:
- ✅ Is excluded from git via `.gitignore`
- ✅ Is loaded only at runtime
- ✅ Never appears in logs or output
- ✅ Is only accessible to your user account

### File Permissions

Ensure proper permissions on sensitive files:
```bash
chmod 600 .env          # Only you can read/write
chmod 644 *.log         # Logs readable by you and group
```

### Best Practices

1. **Never commit `.env`** - It's in `.gitignore` but double-check before pushing
2. **Rotate keys periodically** - Update your API key in Craft and `.env` regularly
3. **Review logs** - Check for any unexpected behavior or errors
4. **Backup before large runs** - Test pattern changes on a small batch first

## License

Private use only.

## Author

Richard Armbrust

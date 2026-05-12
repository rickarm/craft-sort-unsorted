# Craft Unsorted Document Auto-Sorter

Automated Python script that processes unsorted Craft documents, classifies them by content patterns, tags them, and moves them to destination folders. Runs via cron every Friday at 9:00 AM PT.

## Commands

```bash
# Setup (first time)
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Manual run (processes ALL unsorted docs)
./craft_unsorted_sorter.py

# View logs
tail -f ~/Library/Logs/CraftAutoSort/craft_sort_$(date +%Y%m).log

# Activate venv
source venv/bin/activate
```

## Architecture

Single script: `craft_unsorted_sorter.py`. Uses Craft Partner API v1.

**API base URL:** `https://connect.craft.do/links/7MlUnGdilB0/api/v1`

Key endpoints:
```
GET  /documents?location=unsorted  - List unsorted documents
GET  /blocks?id={docId}             - Get document content
GET  /folders                       - List all folders
POST /blocks                        - Add tags to documents
PUT  /documents/move                - Move documents to folders
```

Response structure uses `items` key (not `documents` or `data`).

## Gotchas

- `.env` contains the API key. Never commit it.
- API responses use `items` as the top-level key
- Documents are classified by priority (lower = checked first). See `TAG_MAPPING` dict in the script.
- If a Craft folder doesn't exist, the document gets tagged but not moved (logged as warning).
- Timeout is 30 seconds per request.

## Adding New Document Types

Add to `TAG_MAPPING` in `craft_unsorted_sorter.py`:

```python
"new-tag": {
    "destination_folder": "FOLDER/Subfolder",
    "patterns": [r"regex_pattern1", r"regex_pattern2"],
    "keywords": ["keyword1", "keyword2"],
    "priority": 9,
}
```

Test with a manual run before relying on cron.

## Destination Folders

The script expects these folders in Craft:
- `COACHING/Clients`, `PERSONAL/Home/Family Emails`, `PERSONAL/Finances/Tax`
- `PERSONAL/Travel/Packing Lists`, `REFERENCE/Articles`, `REFERENCE/Research`
- `REFERENCE/People`, `REFERENCE/Companies`

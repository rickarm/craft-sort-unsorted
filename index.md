# craft-sort-unsorted

Automatically sorts unsorted Craft documents by detecting their type (client session, article, tax doc, etc.) and moving them to the appropriate folders. Runs every Friday at 9 AM PT via cron.

## How it works

1. Fetches all documents from Craft's "Unsorted" location via the Partner API
2. Analyzes each document's title and content against regex patterns and keywords
3. Tags the document (e.g. `#client-session`, `#reference-article`)
4. Moves it to the matching folder in Craft

## Key Files

| File | Purpose |
|---|---|
| `craft_unsorted_sorter.py` | Main script — detection logic, API calls, folder filing |
| `setup.sh` | First-time setup: creates venv, installs deps, creates `.env` |
| `setup_cron.sh` | Installs the Friday 9 AM cron job |
| `CLAUDE.md` | Developer guide (pattern system, API notes, debugging) |
| `README.md` | Full user documentation |
| `QUICKSTART.md` | Quick reference card |
| `run_output.log` | Most recent manual run output |
| `venv/` | Python virtual environment (not committed) |

## Document Types Detected

`#client-session` → `COACHING/Clients`
`#family-email` → `PERSONAL/Home/Family Emails`
`#tax` → `PERSONAL/Finances/Tax`
`#packing-list` → `PERSONAL/Travel/Packing Lists`
`#reference-article` → `REFERENCE/Articles`
`#coaching-research` → `REFERENCE/Research`
`#person` → `REFERENCE/People`
`#company` → `REFERENCE/Companies`

## Logs

`~/Library/Logs/CraftAutoSort/craft_sort_YYYYMM.log`

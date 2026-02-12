#!/bin/bash

# Setup script for Craft Auto-Sort cron job
# Schedules the script to run every Friday at 9 AM Pacific Time

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_SCRIPT="$SCRIPT_DIR/craft_unsorted_sorter.py"
PYTHON_PATH="$SCRIPT_DIR/venv/bin/python3"

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script not found at $PYTHON_SCRIPT"
    exit 1
fi

# Make the Python script executable
chmod +x "$PYTHON_SCRIPT"

# Cron expression for every Friday at 9 AM
# 0 9 * * 5 = minute 0, hour 9, any day of month, any month, day 5 (Friday)
CRON_SCHEDULE="0 9 * * 5"

# Full cron job command
# Using virtual environment Python to ensure all dependencies are available
CRON_JOB="$CRON_SCHEDULE $PYTHON_PATH $PYTHON_SCRIPT >> $SCRIPT_DIR/cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -F "$PYTHON_SCRIPT" >/dev/null; then
    echo "Cron job already exists. Removing old entry..."
    crontab -l 2>/dev/null | grep -vF "$PYTHON_SCRIPT" | crontab -
fi

# Add the new cron job
echo "Adding cron job: Every Friday at 9 AM PT"
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo ""
echo "✓ Cron job installed successfully!"
echo ""
echo "Schedule: Every Friday at 9:00 AM Pacific Time"
echo "Script: $PYTHON_SCRIPT"
echo "Logs: $SCRIPT_DIR/cron.log"
echo ""
echo "To view current cron jobs:"
echo "  crontab -l"
echo ""
echo "To remove this cron job:"
echo "  crontab -l | grep -vF '$PYTHON_SCRIPT' | crontab -"
echo ""
echo "Note: Ensure CRAFT_API_KEY environment variable is set in your shell profile"
echo "      or the script will use the hardcoded fallback key."

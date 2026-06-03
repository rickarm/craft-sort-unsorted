#!/Users/richardarmbrust/Dev/craft-sort-unsorted/venv/bin/python3
"""
Craft Unsorted Document Auto-Sorter
Runs every Friday morning to tag and file Unsorted documents.

Configuration:
- Schedule: Every Friday at 9:00 AM PT
- API: Craft Space API (uses your configured API key)
- Tagging: Flat tags (#tag-name)
- Filing: Automatic move to destination folders based on tag mapping
"""

import os
import re
import sys
import logging
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path
import requests
from dotenv import load_dotenv

# ============================================================================
# CONFIGURATION
# ============================================================================

# Load environment variables from .env file
SCRIPT_DIR = Path(__file__).parent.resolve()
load_dotenv(SCRIPT_DIR / ".env")

CRAFT_API_KEY = os.environ.get("CRAFT_API_KEY")
CRAFT_API_BASE_URL = "https://connect.craft.do/links/7MlUnGdilB0/api/v1"

# Logging configuration
LOG_DIR = Path.home() / "Library" / "Logs" / "CraftAutoSort"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"craft_sort_{datetime.now().strftime('%Y%m')}.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Tag mapping: tag -> (destination_folder_id, detection_patterns)
TAG_MAPPING = {
    "client-session": {
        "destination_folder": "COACHING/Clients",
        "patterns": [
            r"^([A-Za-z\s]+)\s*[-–]\s*(\d{1,2}[-/]\d{1,2}|\w+\s+\d{1,2})",  # "Client - Oct 15"
            r"([A-Za-z\s]+)\s+(Session|session|meeting|call)\s*[-–]\s*(\d{4}-\d{2}-\d{2}|\d{1,2}[-/]\d{1,2})",
        ],
        "keywords": ["client", "session", "call", "meeting"],
        "priority": 3,
    },
    "family-email": {
        "destination_folder": "PERSONAL/Home/Family Emails",
        "patterns": [r"^Week of\s+(\w+\s+\d{1,2})", r"^Week of\s+(\d{4}-\d{2}-\d{2})"],
        "keywords": ["week of", "family email"],
        "priority": 4,
    },
    "tax": {
        "destination_folder": "PERSONAL/Finances/Tax",
        "patterns": [r"tax|1099|w2|deduction|irs"],
        "keywords": ["tax", "1099", "w2", "deduction", "irs"],
        "priority": 5,
    },
    "packing-list": {
        "destination_folder": "PERSONAL/Travel/Packing Lists",
        "patterns": [r"packing|packing\s+list|trip\s+packing"],
        "keywords": ["packing", "trip", "travel list"],
        "priority": 6,
    },
    "reference-article": {
        "destination_folder": "REFERENCE/Articles",
        "patterns": [r"http[s]?://", r"article|research|source|blog"],
        "keywords": ["article", "research", "source", "blog"],
        "priority": 7,
    },
    "coaching-research": {
        "destination_folder": "REFERENCE/Research",
        "patterns": [r"coaching|leadership|framework|development"],
        "keywords": ["coaching", "leadership", "framework", "development"],
        "priority": 8,
    },
    "person": {
        "destination_folder": "REFERENCE/People",
        "patterns": [r"(person|people|contact|bio)", r"–\s+(founder|ceo|investor|executive|mentor)"],
        "keywords": ["person", "people", "bio", "founder", "ceo", "investor"],
        "priority": 1,
    },
    "company": {
        "destination_folder": "REFERENCE/Companies",
        "patterns": [r"(company|corp|inc|llc|co\.|portfolio)", r"–\s+(portfolio|startup|company)"],
        "keywords": ["company", "corp", "inc", "startup", "portfolio"],
        "priority": 2,
    },
}

# ============================================================================
# API HELPERS
# ============================================================================


def get_headers():
    """Return headers for Craft API."""
    if not CRAFT_API_KEY:
        logger.error("CRAFT_API_KEY not set. Please set it as an environment variable.")
        sys.exit(1)
    return {
        "Authorization": f"Bearer {CRAFT_API_KEY}",
        "Content-Type": "application/json",
    }


def get_unsorted_documents() -> List[Dict]:
    """Fetch all documents in Unsorted folder."""
    try:
        url = f"{CRAFT_API_BASE_URL}/documents"
        params = {"location": "unsorted"}
        logger.info(f"Fetching unsorted documents from {url}")
        response = requests.get(url, headers=get_headers(), params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        documents = data.get("items", [])
        logger.info(f"Successfully fetched {len(documents)} documents")
        return documents
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch unsorted documents: {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response: {e.response.text}")
        raise


def get_document_content(doc_id: str) -> str:
    """Fetch document content to analyze."""
    try:
        url = f"{CRAFT_API_BASE_URL}/blocks"
        params = {"id": doc_id}
        logger.debug(f"Fetching content for document {doc_id}")
        response = requests.get(url, headers=get_headers(), params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Extract text content from response, including nested blocks.
        # extract_text() reads the top-level "markdown" field plus any children.
        def extract_text(block):
            text = block.get("markdown", "")
            if "content" in block and isinstance(block["content"], list):
                for child in block["content"]:
                    text += " " + extract_text(child)
            return text

        full_text = extract_text(data)
        logger.debug(f"Retrieved {len(full_text)} characters of content")
        return full_text.lower()
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to fetch content for document {doc_id}: {e}")
        return ""


def get_folder_by_path(folder_path: str) -> Optional[str]:
    """Get folder ID for a path like 'COACHING/Clients'."""
    try:
        url = f"{CRAFT_API_BASE_URL}/folders"
        logger.debug(f"Fetching folders to find '{folder_path}'")
        response = requests.get(url, headers=get_headers(), timeout=30)
        response.raise_for_status()
        data = response.json()

        folders = data.get("items", [])
        logger.debug(f"Found {len(folders)} total folders")

        # Build a mapping of folder paths to IDs
        folder_map = {}

        def traverse_folders(folder_list, parent_path=""):
            for folder in folder_list:
                folder_name = folder.get("name", "")
                folder_id = folder.get("id", "")
                current_path = f"{parent_path}/{folder_name}".strip("/")
                folder_map[current_path] = folder_id

                # Recursively process subfolders if they exist
                subfolders = folder.get("folders", [])
                if subfolders:
                    traverse_folders(subfolders, current_path)

        traverse_folders(folders)

        # Look up the folder
        if folder_path in folder_map:
            logger.info(f"Found folder '{folder_path}': {folder_map[folder_path]}")
            return folder_map[folder_path]

        logger.warning(f"Folder '{folder_path}' not found. Available folders: {list(folder_map.keys())[:10]}")
        return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch folders: {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response: {e.response.text}")
        return None


def add_tag_to_document(doc_id: str, tag: str) -> bool:
    """Add a tag to a document by appending it to the content."""
    try:
        # Add the tag as markdown at the end of the document using /blocks endpoint
        tag_text = f"#{tag}"
        url = f"{CRAFT_API_BASE_URL}/blocks"
        payload = {
            "markdown": tag_text,
            "position": {
                "position": "end",
                "pageId": doc_id
            }
        }
        logger.debug(f"Adding tag #{tag} to document {doc_id}")
        response = requests.post(url, headers=get_headers(), json=payload, timeout=30)
        response.raise_for_status()

        logger.info(f"Successfully tagged document {doc_id} with #{tag}")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to tag document {doc_id} with #{tag}: {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response: {e.response.text}")
        return False


def move_document(doc_id: str, destination_folder_id: str) -> bool:
    """Move document to a folder."""
    try:
        url = f"{CRAFT_API_BASE_URL}/documents/move"
        payload = {
            "documentIds": [doc_id],
            "destination": {
                "folderId": destination_folder_id
            }
        }
        logger.debug(f"Moving document {doc_id} to folder {destination_folder_id}")
        response = requests.put(url, headers=get_headers(), json=payload, timeout=30)
        response.raise_for_status()
        logger.info(f"Successfully moved document {doc_id}")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to move document {doc_id}: {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response: {e.response.text}")
        return False


# ============================================================================
# DETECTION LOGIC
# ============================================================================


def detect_tag(doc_name: str, doc_content: Optional[str] = None) -> Optional[str]:
    """Detect the best tag for a document based on name and content."""
    combined_text = (doc_name + " " + (doc_content or "")).lower()

    # Sort by priority (lower number = higher priority)
    sorted_tags = sorted(TAG_MAPPING.items(), key=lambda x: x[1]["priority"])

    for tag, config in sorted_tags:
        # Check keywords
        for keyword in config.get("keywords", []):
            if keyword in combined_text:
                return tag

        # Check patterns
        for pattern in config.get("patterns", []):
            if re.search(pattern, combined_text):
                return tag

    return None


def extract_client_name(doc_name: str) -> Optional[str]:
    """Extract client name from document title."""
    # Pattern: "Client Name - Date" or "Client Name Session - Date"
    match = re.match(r"^([A-Za-z\s&]+?)(?:\s+(?:Session|session|Call|call))?\s*[-–]\s*", doc_name)
    if match:
        return match.group(1).strip()
    return None


# ============================================================================
# MAIN AUTOMATION
# ============================================================================


def run_automation():
    """Main automation function."""
    logger.info("="*70)
    logger.info(f"Craft Unsorted Auto-Sort | {datetime.now().strftime('%Y-%m-%d %H:%M:%S PT')}")
    logger.info("="*70)

    try:
        # Fetch Unsorted documents
        logger.info("📂 Fetching Unsorted documents...")
        docs = get_unsorted_documents()
        logger.info(f"   Found {len(docs)} documents in Unsorted")

        if not docs:
            logger.info("✓ Unsorted folder is empty. Nothing to do!")
            return

        # Process each document
        stats = {
            "processed": 0,
            "tagged": 0,
            "moved": 0,
            "errors": 0,
            "by_tag": {},
        }

        for doc in docs:
            doc_id = doc.get("id")
            doc_name = doc.get("title", "Untitled")

            logger.info(f"Processing: {doc_name}")

            try:
                # Get document content for better analysis
                content = get_document_content(doc_id)

                # Detect tag
                tag = detect_tag(doc_name, content)

                if tag:
                    # Tag the document
                    if add_tag_to_document(doc_id, tag):
                        logger.info(f"  ✓ Tagged as #{tag}")
                        stats["tagged"] += 1
                        stats["by_tag"][tag] = stats["by_tag"].get(tag, 0) + 1

                        # Move document if folder exists
                        destination = TAG_MAPPING[tag]["destination_folder"]
                        logger.info(f"  📁 Moving to: {destination}")

                        folder_id = get_folder_by_path(destination)
                        if folder_id:
                            if move_document(doc_id, folder_id):
                                logger.info(f"  ✓ Moved to: {destination}")
                                stats["moved"] += 1
                            else:
                                logger.warning("  ⚠ Tag added but move failed. Check logs.")
                                stats["errors"] += 1
                        else:
                            logger.warning(f"  ⚠ Tag added. Folder {destination} not found—manual move may be needed.")
                    else:
                        logger.error("  ✗ Failed to tag document")
                        stats["errors"] += 1
                else:
                    logger.info("  → No matching tag. Stays in Unsorted.")
                    # Optionally tag as #general
                    if add_tag_to_document(doc_id, "general"):
                        stats["tagged"] += 1
                        stats["by_tag"]["general"] = stats["by_tag"].get("general", 0) + 1

                stats["processed"] += 1

            except Exception as e:
                logger.error(f"  ✗ Error processing document: {str(e)}", exc_info=True)
                stats["errors"] += 1
                stats["processed"] += 1

        # Print summary
        logger.info("="*70)
        logger.info("Summary")
        logger.info("="*70)
        logger.info(f"Processed:  {stats['processed']} documents")
        logger.info(f"Tagged:     {stats['tagged']} documents")
        logger.info(f"Moved:      {stats['moved']} documents")
        logger.info(f"Errors:     {stats['errors']} documents")
        logger.info("\nBreakdown by tag:")
        for tag, count in sorted(stats["by_tag"].items()):
            logger.info(f"  #{tag}: {count}")
        logger.info("="*70)

    except Exception as e:
        logger.error(f"Fatal error in automation: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run_automation()

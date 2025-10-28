import os
import shutil
from pathlib import Path

# --- CONFIG ---
ROOT_DIR = Path("/Users/shadmansakib/Documents/Thesis") # run this script from the repo root
TARGET_DIR = ROOT_DIR / "research-project"

# Folder structure
folders = {
    "data/raw": [".csv", ".xlsx", ".jsonl"],
    "data/processed": ["merged", "filtered", "cleaned", "tokenized"],
    "notebooks": [".ipynb"],
    "src": [".py"],
    "outputs": ["output", "result", "metrics"],
    "figures": [".png", ".jpg", ".jpeg"],
    "docs/relevant_papers": [".pdf"],
    "website": ["user-story-evaluator"],
}

# --- Setup ---
os.makedirs(TARGET_DIR, exist_ok=True)
log_path = TARGET_DIR / "restructure_log.txt"

def should_ignore(path):
    ignore_names = [".DS_Store", "__pycache__", ".git", "node_modules"]
    return any(ig in str(path) for ig in ignore_names)

def move_file(src_path, dest_folder):
    dest_folder = TARGET_DIR / dest_folder
    os.makedirs(dest_folder, exist_ok=True)
    try:
        shutil.move(str(src_path), dest_folder)
        with open(log_path, "a") as log:
            log.write(f"MOVED: {src_path} → {dest_folder}\n")
    except Exception as e:
        with open(log_path, "a") as log:
            log.write(f"SKIPPED: {src_path} ({e})\n")

# --- Main ---
for path in ROOT_DIR.rglob("*"):
    if path.is_file() and not should_ignore(path):
        name = path.name.lower()
        moved = False

        # match by extension or name keyword
        for folder, patterns in folders.items():
            if any(name.endswith(ext) for ext in patterns if ext.startswith(".")):
                move_file(path, folder)
                moved = True
                break
            if any(keyword in name for keyword in patterns if not keyword.startswith(".")):
                move_file(path, folder)
                moved = True
                break

        # Default handling
        if not moved:
            other_dir = TARGET_DIR / "misc"
            os.makedirs(other_dir, exist_ok=True)
            shutil.move(str(path), other_dir)
            with open(log_path, "a") as log:
                log.write(f"OTHER: {path} → misc\n")

print("✅ Repository reorganized. Check 'research-project/' and 'restructure_log.txt'.")

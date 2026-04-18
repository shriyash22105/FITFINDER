"""
File reorganization script for FitFinder project
Moves unwanted files and directories to _junk folder
Copies documentation to docs folder
"""

import os
import shutil
from pathlib import Path

ROOT_DIR = Path(r"d:\PROJECTS\FITFINDER-")
JUNK_DIR = ROOT_DIR / "_junk"
DOCS_DIR = ROOT_DIR / "docs"

# Items to move to junk
JUNK_ITEMS = [
    "diagrams2",
    "target",
    "uploads",
    "__pycache__",
    "test_cloth.jpg",
    "test_person.jpg",
    "fitfinder.db",
    "users.mv.db",
    "users.trace.db",
    "nul",
    "stop",
    "generated_outfits",
    "tmp",
]

# Documentation files to copy to docs
DOC_FILES = [
    "API_DOCUMENTATION.md",
    "PROJECT_SYNOPSIS.md",
    "INDEX.md",
    "SYNOPSIS.md",
    "TODO.md",
]

print("🔧 FitFinder Project Reorganization")
print("=" * 50)

# Create directories if they don't exist
os.makedirs(JUNK_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

# Move items to junk
print("\n📦 Moving items to _junk/...")
for item in JUNK_ITEMS:
    src = ROOT_DIR / item
    if src.exists():
        try:
            dst = JUNK_DIR / item
            if src.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.move(str(src), str(dst))
                print(f"✓ Moved directory: {item}")
            else:
                if dst.exists():
                    os.remove(dst)
                shutil.move(str(src), str(dst))
                print(f"✓ Moved file: {item}")
        except Exception as e:
            print(f"✗ Failed to move {item}: {e}")
    else:
        print(f"- Skipped (not found): {item}")

# Copy documentation to docs
print("\n📚 Copying documentation to docs/...")
for doc in DOC_FILES:
    src = ROOT_DIR / doc
    if src.exists():
        try:
            dst = DOCS_DIR / doc
            shutil.copy2(str(src), str(dst))
            print(f"✓ Copied: {doc}")
        except Exception as e:
            print(f"✗ Failed to copy {doc}: {e}")
    else:
        print(f"- Skipped (not found): {doc}")

print("\n" + "=" * 50)
print("✅ Project reorganization complete!")
print("\n📁 Current structure:")
print("\nRoot files:")
for item in sorted(os.listdir(ROOT_DIR)):
    path = ROOT_DIR / item
    if path.is_file() and not item.startswith('.'):
        print(f"  - {item}")

print("\nDirectories:")
for item in sorted(os.listdir(ROOT_DIR)):
    path = ROOT_DIR / item
    if path.is_dir() and not item.startswith('.'):
        print(f"  - {item}/")

print(f"\nItems in _junk ({len(os.listdir(JUNK_DIR))}):")
for item in sorted(os.listdir(JUNK_DIR)):
    print(f"  - {item}")

print(f"\nItems in docs ({len(os.listdir(DOCS_DIR))}):")
for item in sorted(os.listdir(DOCS_DIR)):
    print(f"  - {item}")

#!/usr/bin/env python3
"""
Create a .zip file suitable for uploading to https://claude.ai/settings/capabilities

The zip contains:
- SKILL.md (the skill definition)
- scripts/excalidraw_generator.py (the generator library)

Usage:
    python scripts/create_capability_zip.py [output_name]

Output:
    excalidraw-diagrams-capability.zip (or specified name)
"""

import zipfile
import os
from pathlib import Path


def create_capability_zip(output_name: str = "excalidraw-diagrams-capability.zip"):
    """Create the capability zip file."""
    # Get the skill root directory
    script_dir = Path(__file__).parent
    skill_root = script_dir.parent

    # Files to include in the zip
    files_to_include = [
        ("SKILL.md", skill_root / "SKILL.md"),
        ("scripts/excalidraw_generator.py", skill_root / "scripts" / "excalidraw_generator.py"),
    ]

    # Create the zip file
    output_path = skill_root / output_name
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for arcname, filepath in files_to_include:
            if filepath.exists():
                print(f"  Adding: {arcname}")
                zf.write(filepath, arcname)
            else:
                print(f"  WARNING: {filepath} not found, skipping")

    print(f"\nCreated: {output_path}")
    print(f"Size: {output_path.stat().st_size} bytes")
    print(f"\nUpload this file to: https://claude.ai/settings/capabilities")

    return output_path


if __name__ == "__main__":
    import sys
    output_name = sys.argv[1] if len(sys.argv) > 1 else "excalidraw-diagrams-capability.zip"
    create_capability_zip(output_name)

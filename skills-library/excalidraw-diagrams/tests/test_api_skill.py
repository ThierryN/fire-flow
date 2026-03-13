#!/usr/bin/env python3
"""
Test the Excalidraw skill using the Claude API Skills endpoint.

This tests uploading and using the skill via the Claude API (not claude.ai web UI).

Requirements:
    pip install anthropic

Usage:
    ANTHROPIC_API_KEY=sk-... python tests/test_api_skill.py

Environment:
    ANTHROPIC_API_KEY: Your Anthropic API key
"""

import os
import sys
import json
import tempfile
import zipfile
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)


def create_skill_zip(skill_dir: Path) -> Path:
    """Create a zip file of the skill for upload."""
    zip_path = Path(tempfile.mktemp(suffix=".zip"))

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add SKILL.md
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            zf.write(skill_md, "excalidraw-diagrams/SKILL.md")

        # Add generator script
        generator = skill_dir / "scripts" / "excalidraw_generator.py"
        if generator.exists():
            zf.write(generator, "excalidraw-diagrams/scripts/excalidraw_generator.py")

    return zip_path


def test_skill_upload_and_use():
    """Test uploading and using the Excalidraw skill via API."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Find skill directory
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent

    print(f"Skill directory: {skill_dir}")
    print(f"SKILL.md exists: {(skill_dir / 'SKILL.md').exists()}")
    print(f"Generator exists: {(skill_dir / 'scripts' / 'excalidraw_generator.py').exists()}")

    # Create zip for upload
    print("\n1. Creating skill zip...")
    zip_path = create_skill_zip(skill_dir)
    print(f"   Created: {zip_path} ({zip_path.stat().st_size} bytes)")

    skill_id = None
    try:
        # Upload skill
        print("\n2. Uploading skill to Claude API...")
        with open(zip_path, "rb") as f:
            skill = client.beta.skills.create(
                display_title="Excalidraw Diagrams (Test)",
                files=[("skill.zip", f)],
                betas=["skills-2025-10-02"]
            )
        skill_id = skill.id
        print(f"   Skill ID: {skill_id}")
        print(f"   Version: {skill.latest_version}")

        # Test using the skill
        print("\n3. Testing skill with Messages API...")
        response = client.beta.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            betas=["code-execution-2025-08-25", "skills-2025-10-02"],
            container={
                "skills": [{
                    "type": "custom",
                    "skill_id": skill_id,
                    "version": "latest"
                }]
            },
            messages=[{
                "role": "user",
                "content": """Using the excalidraw-diagrams skill, create a simple diagram with:
                - A "User" box on the left
                - An "API" box in the middle
                - A "Database" box on the right
                - Arrows connecting them

                Save it as test_output.excalidraw and print the JSON content."""
            }],
            tools=[{
                "type": "code_execution_20250825",
                "name": "code_execution"
            }]
        )

        print(f"   Stop reason: {response.stop_reason}")
        print(f"   Content blocks: {len(response.content)}")

        # Check response for success indicators
        response_text = ""
        for block in response.content:
            if hasattr(block, 'text'):
                response_text += block.text

        if "excalidraw" in response_text.lower() or "diagram" in response_text.lower():
            print("\n4. SUCCESS: Skill appears to be working!")
            print(f"   Response preview: {response_text[:500]}...")
        else:
            print("\n4. WARNING: Response may not indicate skill usage")
            print(f"   Response: {response_text[:500]}...")

    except anthropic.BadRequestError as e:
        print(f"\nERROR: Bad request - {e}")
        print("This may indicate the skill format is incorrect.")
        sys.exit(1)
    except anthropic.APIError as e:
        print(f"\nERROR: API error - {e}")
        sys.exit(1)
    finally:
        # Clean up: delete the test skill
        if skill_id:
            print("\n5. Cleaning up: deleting test skill...")
            try:
                # First delete all versions
                versions = client.beta.skills.versions.list(
                    skill_id=skill_id,
                    betas=["skills-2025-10-02"]
                )
                for version in versions.data:
                    client.beta.skills.versions.delete(
                        skill_id=skill_id,
                        version=version.version,
                        betas=["skills-2025-10-02"]
                    )
                # Then delete the skill
                client.beta.skills.delete(
                    skill_id=skill_id,
                    betas=["skills-2025-10-02"]
                )
                print("   Skill deleted successfully")
            except Exception as e:
                print(f"   Warning: Failed to delete skill - {e}")

        # Clean up zip file
        if zip_path.exists():
            zip_path.unlink()

    print("\nTest completed!")


if __name__ == "__main__":
    test_skill_upload_and_use()

#!/usr/bin/env python3
"""
Google Drive helper for excalidraw-diagrams skill.
Wraps drive_manager.rb from the google-docs skill.
"""

import subprocess
import json
import os
from pathlib import Path


DRIVE_MANAGER = Path.home() / ".claude" / "skills" / "google-docs" / "scripts" / "drive_manager.rb"


def _run_drive_command(args: list[str]) -> dict:
    """Run drive_manager.rb with arguments and return parsed JSON result."""
    if not DRIVE_MANAGER.exists():
        return {
            "status": "error",
            "error_code": "DRIVE_MANAGER_NOT_FOUND",
            "message": f"drive_manager.rb not found at {DRIVE_MANAGER}. Install google-docs skill first."
        }

    cmd = ["ruby", str(DRIVE_MANAGER)] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "error_code": "TIMEOUT",
            "message": "Drive operation timed out"
        }
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "error_code": "PARSE_ERROR",
            "message": f"Failed to parse drive_manager output: {e}",
            "raw_output": result.stdout if 'result' in dir() else None
        }
    except Exception as e:
        return {
            "status": "error",
            "error_code": "UNKNOWN_ERROR",
            "message": str(e)
        }


def upload_to_drive(file_path: str, folder_id: str = None, name: str = None) -> dict:
    """
    Upload a file to Google Drive.

    Args:
        file_path: Local path to the file to upload
        folder_id: Optional Drive folder ID to upload to
        name: Optional name for the file in Drive (defaults to filename)

    Returns:
        dict with status, file info including id, web_view_link, etc.
    """
    args = ["upload", "--file", file_path]
    if folder_id:
        args.extend(["--folder-id", folder_id])
    if name:
        args.extend(["--name", name])

    return _run_drive_command(args)


def download_from_drive(file_id: str, output_path: str) -> dict:
    """
    Download a file from Google Drive.

    Args:
        file_id: Drive file ID
        output_path: Local path to save the file

    Returns:
        dict with status and file info
    """
    return _run_drive_command(["download", "--file-id", file_id, "--output", output_path])


def update_in_drive(file_id: str, file_path: str, name: str = None) -> dict:
    """
    Update an existing file in Google Drive.

    Args:
        file_id: Drive file ID to update
        file_path: Local path to the new file content
        name: Optional new name for the file

    Returns:
        dict with status and updated file info
    """
    args = ["update", "--file-id", file_id, "--file", file_path]
    if name:
        args.extend(["--name", name])

    return _run_drive_command(args)


def share_file(file_id: str, email: str = None, role: str = "reader",
               share_type: str = None) -> dict:
    """
    Share a file in Google Drive.

    Args:
        file_id: Drive file ID
        email: Email address to share with (for user sharing)
        role: Permission role (reader, writer, commenter)
        share_type: Permission type (user, anyone, domain)

    Returns:
        dict with status and sharing info including web_view_link
    """
    args = ["share", "--file-id", file_id, "--role", role]
    if email:
        args.extend(["--email", email])
    if share_type:
        args.extend(["--type", share_type])

    return _run_drive_command(args)


def search_excalidraw_files(query: str = None, max_results: int = 100) -> dict:
    """
    Search for Excalidraw files in Google Drive.

    Args:
        query: Additional search query (combined with .excalidraw filter)
        max_results: Maximum number of results

    Returns:
        dict with status and list of matching files
    """
    base_query = "name contains '.excalidraw'"
    if query:
        full_query = f"{base_query} and {query}"
    else:
        full_query = base_query

    return _run_drive_command(["search", "--query", full_query, "--max-results", str(max_results)])


def get_file_metadata(file_id: str) -> dict:
    """
    Get metadata for a file in Google Drive.

    Args:
        file_id: Drive file ID

    Returns:
        dict with status and file metadata
    """
    return _run_drive_command(["get-metadata", "--file-id", file_id])


def create_diagrams_folder(name: str = "Excalidraw Diagrams", parent_id: str = None) -> dict:
    """
    Create a folder for storing Excalidraw diagrams.

    Args:
        name: Folder name
        parent_id: Optional parent folder ID

    Returns:
        dict with status and folder info
    """
    args = ["create-folder", "--name", name]
    if parent_id:
        args.extend(["--parent-id", parent_id])

    return _run_drive_command(args)


def get_excalidraw_edit_url(file_id: str, make_public: bool = False) -> str:
    """
    Get URL to edit an Excalidraw file.

    Args:
        file_id: Drive file ID
        make_public: If True, share the file publicly first

    Returns:
        URL to open the file in Excalidraw
    """
    if make_public:
        share_file(file_id, share_type="anyone", role="reader")

    # Direct download URL for Excalidraw to load
    download_url = f"https://drive.google.com/uc?id={file_id}&export=download"

    # Excalidraw can load JSON from URL
    return f"https://excalidraw.com/#json={download_url}"


# Convenience class for use with Diagram
class DriveUploader:
    """Helper class for uploading diagrams to Drive."""

    def __init__(self, folder_id: str = None):
        """
        Initialize uploader.

        Args:
            folder_id: Default folder ID for uploads
        """
        self.folder_id = folder_id
        self.last_upload = None

    def upload(self, file_path: str, name: str = None, share_public: bool = False) -> dict:
        """
        Upload a diagram and optionally share it.

        Args:
            file_path: Path to .excalidraw file
            name: Optional custom name
            share_public: If True, make the file publicly accessible

        Returns:
            dict with file info and edit URL
        """
        result = upload_to_drive(file_path, folder_id=self.folder_id, name=name)

        if result.get("status") == "success":
            file_id = result["file"]["id"]

            if share_public:
                share_result = share_file(file_id, share_type="anyone", role="reader")
                result["share"] = share_result

            result["edit_url"] = get_excalidraw_edit_url(file_id, make_public=False)
            self.last_upload = result

        return result

    def update(self, file_id: str, file_path: str) -> dict:
        """
        Update an existing diagram in Drive.

        Args:
            file_id: Existing Drive file ID
            file_path: Path to updated .excalidraw file

        Returns:
            dict with updated file info
        """
        result = update_in_drive(file_id, file_path)
        if result.get("status") == "success":
            result["edit_url"] = get_excalidraw_edit_url(file_id)
        return result


if __name__ == "__main__":
    # Test the helper
    import sys

    if len(sys.argv) < 2:
        print("Usage: drive_helper.py <command> [args]")
        print("Commands: search, upload <file>, download <file_id> <output>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "search":
        result = search_excalidraw_files()
        print(json.dumps(result, indent=2))

    elif cmd == "upload" and len(sys.argv) >= 3:
        result = upload_to_drive(sys.argv[2])
        print(json.dumps(result, indent=2))
        if result.get("status") == "success":
            print(f"\nEdit URL: {get_excalidraw_edit_url(result['file']['id'])}")

    elif cmd == "download" and len(sys.argv) >= 4:
        result = download_from_drive(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command or missing arguments: {cmd}")
        sys.exit(1)

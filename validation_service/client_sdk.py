#!/usr/bin/env python3
"""
Project Validation Service Client SDK
Easy-to-use Python client for the validation service
"""

import json
import os
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests


class ValidationClient:
    """Client for the Project Validation Service"""

    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def health_check(self) -> Dict[str, Any]:
        """Check if the validation service is running"""
        try:
            response = self.session.get(f"{self.base_url}/")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ConnectionError(f"Cannot connect to validation service: {e}")

    def validate_project_file(
        self,
        file_path: Union[str, Path],
        project_name: Optional[str] = None,
        validation_profile: str = "comprehensive",
        wait_for_completion: bool = True,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """
        Validate a project from a ZIP/TAR file

        Args:
            file_path: Path to the project archive
            project_name: Optional project name
            validation_profile: Validation profile to use
            wait_for_completion: Whether to wait for results
            timeout: Timeout in seconds

        Returns:
            Validation results or status
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.suffix.lower() in [".zip", ".tar", ".gz"]:
            raise ValueError("File must be a ZIP or TAR archive")

        # Upload file
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "application/octet-stream")}
            data = {
                "project_name": project_name or file_path.stem,
                "validation_profile": validation_profile,
            }

            response = self.session.post(f"{self.base_url}/validate/upload", files=files, data=data)
            response.raise_for_status()
            result = response.json()

        validation_id = result["validation_id"]

        if not wait_for_completion:
            return result

        # Wait for completion
        return self._wait_for_completion(validation_id, timeout)

    def validate_project_folder(
        self,
        folder_path: Union[str, Path],
        project_name: Optional[str] = None,
        validation_profile: str = "comprehensive",
        wait_for_completion: bool = True,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """
        Validate a project from a local folder

        Args:
            folder_path: Path to the project folder
            project_name: Optional project name
            validation_profile: Validation profile to use
            wait_for_completion: Whether to wait for results
            timeout: Timeout in seconds

        Returns:
            Validation results or status
        """
        folder_path = Path(folder_path)

        if not folder_path.exists() or not folder_path.is_dir():
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        # Read folder contents
        folder_contents = self._read_folder_contents(folder_path)

        # Send for validation
        data = {
            "project_name": project_name or folder_path.name,
            "folder_contents": folder_contents,
            "validation_profile": validation_profile,
        }

        response = self.session.post(f"{self.base_url}/validate/folder", json=data)
        response.raise_for_status()
        result = response.json()

        validation_id = result["validation_id"]

        if not wait_for_completion:
            return result

        # Wait for completion
        return self._wait_for_completion(validation_id, timeout)

    def validate_git_repository(
        self,
        git_url: str,
        project_name: Optional[str] = None,
        branch: str = "main",
        validation_profile: str = "comprehensive",
        wait_for_completion: bool = True,
        timeout: int = 600,
    ) -> Dict[str, Any]:
        """
        Validate a Git repository

        Args:
            git_url: Git repository URL
            project_name: Optional project name
            branch: Git branch to analyze
            validation_profile: Validation profile to use
            wait_for_completion: Whether to wait for results
            timeout: Timeout in seconds

        Returns:
            Validation results or status
        """
        data = {
            "git_url": git_url,
            "project_name": project_name,
            "branch": branch,
            "validation_profile": validation_profile,
        }

        response = self.session.post(f"{self.base_url}/validate/git", json=data)
        response.raise_for_status()
        result = response.json()

        validation_id = result["validation_id"]

        if not wait_for_completion:
            return result

        # Wait for completion
        return self._wait_for_completion(validation_id, timeout)

    def get_validation_status(self, validation_id: str) -> Dict[str, Any]:
        """Get validation status"""
        response = self.session.get(f"{self.base_url}/validate/{validation_id}/status")
        response.raise_for_status()
        return response.json()

    def get_validation_results(self, validation_id: str) -> Dict[str, Any]:
        """Get validation results"""
        response = self.session.get(f"{self.base_url}/validate/{validation_id}/results")
        response.raise_for_status()
        return response.json()

    def get_validation_report(self, validation_id: str) -> Dict[str, Any]:
        """Get detailed validation report"""
        response = self.session.get(f"{self.base_url}/validate/{validation_id}/report")
        response.raise_for_status()
        return response.json()

    def download_report(
        self, validation_id: str, output_path: Optional[Union[str, Path]] = None
    ) -> Path:
        """Download validation report as markdown file"""
        response = self.session.get(f"{self.base_url}/validate/{validation_id}/report/download")
        response.raise_for_status()

        if output_path is None:
            output_path = Path(f"validation-report-{validation_id}.md")
        else:
            output_path = Path(output_path)

        with open(output_path, "wb") as f:
            f.write(response.content)

        return output_path

    def _wait_for_completion(self, validation_id: str, timeout: int) -> Dict[str, Any]:
        """Wait for validation to complete"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.get_validation_status(validation_id)

            if status["status"] == "completed":
                return self.get_validation_results(validation_id)
            elif status["status"] == "failed":
                raise RuntimeError(f"Validation failed: {status.get('message', 'Unknown error')}")

            time.sleep(2)  # Poll every 2 seconds

        raise TimeoutError(f"Validation timed out after {timeout} seconds")

    def _read_folder_contents(self, folder_path: Path) -> Dict[str, Any]:
        """Read folder contents for validation"""
        contents = {"files": [], "directories": [], "file_contents": {}}

        # Skip common ignore patterns
        ignore_dirs = {
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            "dist",
            "build",
        }
        ignore_files = {".DS_Store", "Thumbs.db"}

        for root, dirs, files in os.walk(folder_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]

            for file in files:
                if file in ignore_files:
                    continue

                file_path = Path(root) / file
                relative_path = file_path.relative_to(folder_path)
                contents["files"].append(str(relative_path))

                # Read text files (with size limit)
                if self._is_text_file(file) and file_path.stat().st_size < 1024 * 1024:  # 1MB limit
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            contents["file_contents"][str(relative_path)] = f.read()
                    except (UnicodeDecodeError, PermissionError):
                        pass  # Skip files that can't be read

            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                relative_path = dir_path.relative_to(folder_path)
                contents["directories"].append(str(relative_path))

        return contents

    def _is_text_file(self, filename: str) -> bool:
        """Check if file is likely a text file"""
        text_extensions = {
            ".py",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".java",
            ".cs",
            ".php",
            ".rb",
            ".go",
            ".rs",
            ".html",
            ".css",
            ".scss",
            ".sass",
            ".less",
            ".vue",
            ".svelte",
            ".json",
            ".xml",
            ".yaml",
            ".yml",
            ".toml",
            ".ini",
            ".cfg",
            ".conf",
            ".md",
            ".txt",
            ".rst",
            ".sql",
            ".sh",
            ".bat",
            ".ps1",
            ".dockerfile",
            ".gitignore",
            ".gitattributes",
            ".editorconfig",
        }

        ext = Path(filename).suffix.lower()
        return (
            ext in text_extensions
            or "makefile" in filename.lower()
            or "dockerfile" in filename.lower()
        )


# Convenience functions
def validate_project(
    path: Union[str, Path],
    project_name: Optional[str] = None,
    service_url: str = "http://localhost:8002",
) -> Dict[str, Any]:
    """
    Quick validation of a project (auto-detects file vs folder)

    Args:
        path: Path to project file or folder
        project_name: Optional project name
        service_url: Validation service URL

    Returns:
        Validation results
    """
    client = ValidationClient(service_url)
    path = Path(path)

    if path.is_file():
        return client.validate_project_file(path, project_name)
    elif path.is_dir():
        return client.validate_project_folder(path, project_name)
    else:
        raise ValueError(f"Path does not exist: {path}")


def validate_git_repo(
    git_url: str,
    project_name: Optional[str] = None,
    branch: str = "main",
    service_url: str = "http://localhost:8002",
) -> Dict[str, Any]:
    """
    Quick validation of a Git repository

    Args:
        git_url: Git repository URL
        project_name: Optional project name
        branch: Git branch to analyze
        service_url: Validation service URL

    Returns:
        Validation results
    """
    client = ValidationClient(service_url)
    return client.validate_git_repository(git_url, project_name, branch)


if __name__ == "__main__":
    # Example usage
    client = ValidationClient()

    # Check service health
    try:
        health = client.health_check()
        print("✅ Validation service is running")
        print(f"Service: {health['service']} v{health['version']}")
    except ConnectionError as e:
        print(f"❌ Service not available: {e}")
        exit(1)

    # Example validation
    import sys

    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        print(f"\n🔍 Validating project: {project_path}")

        try:
            results = validate_project(project_path)

            print(f"\n📊 Validation Results:")
            print(f"Project: {results['project_name']}")
            print(f"Security Score: {results['scores']['security']}/100")
            print(f"Quality Score: {results['scores']['quality']}/100")
            print(f"Architecture Score: {results['scores']['architecture']}/100")

            if results["recommendations"]:
                print(f"\n💡 Top Recommendations:")
                for i, rec in enumerate(results["recommendations"][:3], 1):
                    print(f"{i}. {rec}")

        except Exception as e:
            print(f"❌ Validation failed: {e}")
    else:
        print("Usage: python client_sdk.py <project_path>")

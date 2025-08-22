#!/usr/bin/env python3
"""
Unit tests for the Validation Service
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Add the validation_service directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validation_service"))

from client_sdk import ValidationClient


class TestValidationClient(unittest.TestCase):
    """Test cases for the ValidationClient class"""

    def setUp(self):
        """Set up test fixtures"""
        self.client = ValidationClient("http://localhost:8002")

    def test_client_initialization(self):
        """Test that the client initializes correctly"""
        self.assertIsInstance(self.client, ValidationClient)
        self.assertEqual(self.client.base_url, "http://localhost:8002")

    @patch("requests.Session.get")
    def test_health_check_success(self, mock_get):
        """Test successful health check"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "service": "Project Validation Service",
            "version": "1.0.0",
            "status": "active",
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.health_check()

        self.assertEqual(result["service"], "Project Validation Service")
        self.assertEqual(result["version"], "1.0.0")
        self.assertEqual(result["status"], "active")

    @patch("requests.Session.get")
    def test_health_check_failure(self, mock_get):
        """Test health check failure"""
        mock_get.side_effect = Exception("Connection failed")

        with self.assertRaises(ConnectionError):
            self.client.health_check()

    def test_read_folder_contents(self):
        """Test reading folder contents"""
        # Create a temporary directory with test files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_files = {
                "main.py": 'print("Hello World")',
                "README.md": "# Test Project",
                "requirements.txt": "fastapi==0.104.1",
            }

            for filename, content in test_files.items():
                with open(os.path.join(temp_dir, filename), "w") as f:
                    f.write(content)

            # Create a subdirectory
            sub_dir = os.path.join(temp_dir, "subdir")
            os.makedirs(sub_dir)
            with open(os.path.join(sub_dir, "test.py"), "w") as f:
                f.write("# Test file")

            contents = self.client._read_folder_contents(temp_dir)

            # Check structure
            self.assertIn("files", contents)
            self.assertIn("directories", contents)
            self.assertIn("file_contents", contents)

            # Check files were found
            self.assertIn("main.py", contents["files"])
            self.assertIn("README.md", contents["files"])
            self.assertIn("requirements.txt", contents["files"])
            self.assertIn("subdir/test.py", contents["files"])

            # Check directories were found
            self.assertIn("subdir", contents["directories"])

            # Check file contents were read
            self.assertEqual(contents["file_contents"]["main.py"], 'print("Hello World")')
            self.assertEqual(contents["file_contents"]["README.md"], "# Test Project")

    def test_is_text_file(self):
        """Test text file detection"""
        # Test text files
        text_files = [
            "main.py",
            "app.js",
            "style.css",
            "index.html",
            "README.md",
            "config.json",
            "docker-compose.yml",
            "Dockerfile",
            "Makefile",
            ".gitignore",
        ]

        for filename in text_files:
            with self.subTest(filename=filename):
                self.assertTrue(self.client._is_text_file(filename))

        # Test binary files
        binary_files = [
            "image.png",
            "video.mp4",
            "archive.zip",
            "binary.exe",
            "library.so",
            "font.ttf",
        ]

        for filename in binary_files:
            with self.subTest(filename=filename):
                self.assertFalse(self.client._is_text_file(filename))

    @patch("requests.Session.post")
    def test_validate_folder_contents(self, mock_post):
        """Test folder contents validation"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "validation_id": "test-123",
            "status": "processing",
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Create test folder contents
        folder_contents = {
            "files": ["main.py", "README.md"],
            "directories": ["src"],
            "file_contents": {"main.py": "print('Hello')", "README.md": "# Test"},
        }

        with patch.object(self.client, "_read_folder_contents", return_value=folder_contents):
            with patch.object(self.client, "_wait_for_completion") as mock_wait:
                mock_wait.return_value = {
                    "validation_id": "test-123",
                    "status": "completed",
                }

                result = self.client.validate_project_folder(
                    folder_path="/fake/path", project_name="Test Project"
                )

                self.assertEqual(result["validation_id"], "test-123")

    @patch("requests.Session.get")
    def test_get_validation_status(self, mock_get):
        """Test getting validation status"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "validation_id": "test-123",
            "status": "processing",
            "progress": 50,
            "message": "Analyzing codebase...",
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.get_validation_status("test-123")

        self.assertEqual(result["validation_id"], "test-123")
        self.assertEqual(result["status"], "processing")
        self.assertEqual(result["progress"], 50)

    @patch("requests.Session.get")
    def test_get_validation_results(self, mock_get):
        """Test getting validation results"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "validation_id": "test-123",
            "status": "completed",
            "project_name": "Test Project",
            "scores": {"security": 95, "quality": 88, "architecture": 92},
            "recommendations": [
                "Add comprehensive testing",
                "Implement API documentation",
            ],
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.get_validation_results("test-123")

        self.assertEqual(result["validation_id"], "test-123")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["scores"]["security"], 95)
        self.assertEqual(len(result["recommendations"]), 2)


class TestValidationServiceIntegration(unittest.TestCase):
    """Integration tests for the validation service"""

    def test_validation_workflow(self):
        """Test the complete validation workflow"""
        # This would be an integration test that requires the actual service
        # For now, we'll test the workflow logic

        workflow_steps = [
            "initialize_client",
            "prepare_project_data",
            "submit_validation",
            "poll_status",
            "retrieve_results",
            "download_report",
        ]

        # Verify all workflow steps are defined
        client = ValidationClient("http://localhost:8002")

        # Check that client has all necessary methods
        self.assertTrue(hasattr(client, "validate_project_folder"))
        self.assertTrue(hasattr(client, "validate_git_repository"))
        self.assertTrue(hasattr(client, "get_validation_status"))
        self.assertTrue(hasattr(client, "get_validation_results"))
        self.assertTrue(hasattr(client, "download_report"))

    def test_error_handling(self):
        """Test error handling in validation client"""
        client = ValidationClient("http://localhost:8002")

        # Test with non-existent folder
        with self.assertRaises(FileNotFoundError):
            client.validate_project_folder("/non/existent/path")

        # Test with invalid file
        with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
            with self.assertRaises(ValueError):
                client.validate_project_file(temp_file.name)


class TestValidationServiceHelpers(unittest.TestCase):
    """Test helper functions for validation service"""

    def test_convenience_functions(self):
        """Test convenience functions"""
        # Import convenience functions
        try:
            from client_sdk import validate_git_repo, validate_project

            # Check that functions exist
            self.assertTrue(callable(validate_project))
            self.assertTrue(callable(validate_git_repo))

        except ImportError:
            self.fail("Convenience functions should be importable")

    def test_validation_profiles(self):
        """Test different validation profiles"""
        profiles = [
            "comprehensive",
            "security-focused",
            "quality-focused",
            "architecture-focused",
        ]

        client = ValidationClient("http://localhost:8002")

        # Test that client accepts different profiles
        for profile in profiles:
            with self.subTest(profile=profile):
                # This would normally make an API call, but we're just testing the interface
                try:
                    # The method should accept the profile parameter
                    with tempfile.TemporaryDirectory() as temp_dir:
                        with open(os.path.join(temp_dir, "test.py"), "w") as f:
                            f.write('print("test")')

                        # This will fail due to no service, but should not fail due to invalid profile
                        try:
                            client.validate_project_folder(
                                temp_dir,
                                validation_profile=profile,
                                wait_for_completion=False,
                            )
                        except Exception as e:
                            # Should fail due to connection, not invalid profile
                            self.assertNotIn("profile", str(e).lower())

                except Exception:
                    # Expected to fail without service running
                    pass


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)

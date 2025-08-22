#!/usr/bin/env python3
"""
Unit tests for the Application Analyzer
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add the web_app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "web_app"))

from app_analyzer import ApplicationAnalyzer


class TestApplicationAnalyzer(unittest.TestCase):
    """Test cases for the ApplicationAnalyzer class"""

    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = ApplicationAnalyzer()

    def test_analyzer_initialization(self):
        """Test that the analyzer initializes correctly"""
        self.assertIsInstance(self.analyzer, ApplicationAnalyzer)
        self.assertIn("frontend", self.analyzer.file_patterns)
        self.assertIn("backend", self.analyzer.file_patterns)
        self.assertIn("testing", self.analyzer.quality_indicators)

    def test_security_score_calculation(self):
        """Test security score calculation"""
        # Test with no security features
        score = self.analyzer._calculate_fair_security_score([])
        self.assertEqual(score, 50)  # Base score

        # Test with authentication
        score = self.analyzer._calculate_fair_security_score(["authentication"])
        self.assertEqual(score, 75)  # Base + 25

        # Test with all features
        all_features = [
            "authentication",
            "validation",
            "encryption",
            "security_headers",
        ]
        score = self.analyzer._calculate_fair_security_score(all_features)
        self.assertEqual(score, 100)  # Should cap at 100

    def test_quality_score_calculation(self):
        """Test quality score calculation"""
        # Test with no practices
        score = self.analyzer._calculate_fair_quality_score([])
        self.assertEqual(score, 70)  # Base score

        # Test with documentation
        score = self.analyzer._calculate_fair_quality_score(["documentation"])
        self.assertEqual(score, 95)  # Base + 15 + 10 bonus

        # Test with multiple practices
        practices = ["documentation", "testing", "ci_cd"]
        score = self.analyzer._calculate_fair_quality_score(practices)
        self.assertEqual(score, 100)  # Should cap at 100

    def test_architecture_score_calculation(self):
        """Test architecture score calculation with mock paths"""
        # Create a temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some directories that should be detected
            os.makedirs(os.path.join(temp_dir, "web_app"))
            os.makedirs(os.path.join(temp_dir, "static"))
            os.makedirs(os.path.join(temp_dir, "templates"))

            # Create some files
            Path(os.path.join(temp_dir, "requirements.txt")).touch()
            Path(os.path.join(temp_dir, "Dockerfile")).touch()
            Path(os.path.join(temp_dir, "docker-compose.yml")).touch()

            score = self.analyzer._calculate_comprehensive_architecture_score(temp_dir)

            # Should get points for structure
            self.assertGreaterEqual(score, 60)  # At least base score
            self.assertLessEqual(score, 100)  # Should not exceed 100

    def test_folder_contents_analysis(self):
        """Test analysis of folder contents"""
        folder_contents = {
            "files": [
                "main.py",
                "requirements.txt",
                "README.md",
                "test_main.py",
                "Dockerfile",
            ],
            "directories": ["web_app", "static", "templates", "tests"],
            "file_contents": {
                "main.py": "from fastapi import FastAPI\napp = FastAPI()",
                "requirements.txt": "fastapi==0.104.1\nuvicorn==0.24.0",
                "README.md": "# My Project\nThis is a test project",
                "test_main.py": "import unittest\nclass TestMain(unittest.TestCase):\n    pass",
            },
        }

        analysis = self.analyzer.analyze_folder_contents(folder_contents)

        # Check that analysis completed successfully
        self.assertIn("project_structure", analysis)
        self.assertIn("detected_technologies", analysis)
        self.assertIn("quality_assessment", analysis)
        self.assertIn("security_analysis", analysis)

        # Check that testing was detected
        quality = analysis["quality_assessment"]
        self.assertIn("testing", quality["implemented_practices"])

        # Check that documentation was detected
        self.assertIn("documentation", quality["implemented_practices"])

    def test_technology_detection(self):
        """Test technology detection from file patterns"""
        folder_contents = {
            "files": ["package.json", "main.py", "Dockerfile", "index.html"],
            "directories": [],
            "file_contents": {
                "package.json": '{"dependencies": {"express": "^4.18.0"}}',
                "main.py": "from fastapi import FastAPI",
                "Dockerfile": "FROM python:3.11",
                "index.html": "<html><body>Hello</body></html>",
            },
        }

        technologies = self.analyzer._detect_technologies_from_contents(folder_contents)

        # Should detect Python backend
        self.assertIn("backend", technologies)
        self.assertIn("python", technologies["backend"])

        # Should detect HTML frontend
        self.assertIn("frontend", technologies)
        self.assertIn("html_css", technologies["frontend"])

        # Should detect Docker
        self.assertIn("devops", technologies)
        self.assertIn("docker", technologies["devops"])

    def test_grading_scale_explanation(self):
        """Test that grading scale explanation is available"""
        explanation = self.analyzer.get_grading_scale_explanation()

        self.assertIsInstance(explanation, str)
        self.assertIn("Security Score", explanation)
        self.assertIn("Quality Score", explanation)
        self.assertIn("Architecture Score", explanation)
        self.assertIn("Base Score", explanation)

    def test_project_boost_logic(self):
        """Test the quality project boost logic"""
        # Create a mock analysis that should get boosted
        analysis = {
            "project_structure": {"directories": ["web_app/"]},
            "detected_technologies": {"devops": ["docker"], "backend": ["python"]},
            "quality_assessment": {
                "quality_score": 75,
                "implemented_practices": ["documentation"],
            },
            "architecture_insights": {
                "architectural_score": 75,
                "patterns": ["Layered"],
            },
        }

        boosted_analysis = self.analyzer._boost_scores_for_quality_projects(analysis)

        # Should boost scores to at least 90
        self.assertGreaterEqual(
            boosted_analysis["quality_assessment"]["quality_score"], 90
        )
        self.assertGreaterEqual(
            boosted_analysis["architecture_insights"]["architectural_score"], 90
        )


class TestAnalyzerIntegration(unittest.TestCase):
    """Integration tests for the analyzer"""

    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = ApplicationAnalyzer()

    def test_full_analysis_pipeline(self):
        """Test the complete analysis pipeline"""
        # Create a realistic project structure
        folder_contents = {
            "files": [
                "web_app/main.py",
                "web_app/app_analyzer.py",
                "static/app.js",
                "templates/index.html",
                "requirements.txt",
                "Dockerfile",
                "docker-compose.yml",
                "README.md",
                "tests/test_main.py",
            ],
            "directories": ["web_app", "static", "templates", "tests"],
            "file_contents": {
                "web_app/main.py": """
from fastapi import FastAPI, HTTPException
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

@app.get("/")
async def root():
    try:
        return {"message": "Hello World"}
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal error")
""",
                "requirements.txt": "fastapi==0.104.1\nuvicorn==0.24.0",
                "README.md": "# My Project\n\nThis is a comprehensive project with proper documentation.",
                "tests/test_main.py": "import unittest\nfrom web_app.main import app",
            },
        }

        analysis = self.analyzer.analyze_folder_contents(folder_contents)

        # Verify all major components are present
        self.assertIn("project_structure", analysis)
        self.assertIn("detected_technologies", analysis)
        self.assertIn("application_type", analysis)
        self.assertIn("security_analysis", analysis)
        self.assertIn("quality_assessment", analysis)
        self.assertIn("architecture_insights", analysis)

        # Verify high scores for this well-structured project
        self.assertGreaterEqual(analysis["security_analysis"]["security_score"], 80)
        self.assertGreaterEqual(analysis["quality_assessment"]["quality_score"], 90)
        self.assertGreaterEqual(
            analysis["architecture_insights"]["architectural_score"], 80
        )

        # Verify testing is detected
        self.assertIn(
            "testing", analysis["quality_assessment"]["implemented_practices"]
        )


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)

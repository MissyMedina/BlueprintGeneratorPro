#!/usr/bin/env python3
"""
Integration tests for the complete Guidance Blueprint Kit Pro system
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add project directories to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "web_app"))
sys.path.insert(0, str(project_root / "validation_service"))

from app_analyzer import ApplicationAnalyzer
from content_generator import ContentGenerator


class TestSystemIntegration(unittest.TestCase):
    """Integration tests for the complete system"""

    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = ApplicationAnalyzer()
        self.generator = ContentGenerator()

    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""

        # Step 1: Create a mock project structure
        project_data = {
            "project": "Integration Test Project",
            "description": "A comprehensive test of the entire system",
            "components": ["frontend", "backend", "database"],
            "docType": "prd",
            "focusArea": "technical",
            "customAnswers": {
                "target_audience": "Developers and QA engineers",
                "key_features": "Automated testing, CI/CD integration",
                "success_metrics": "Test coverage, build success rate",
            },
        }

        # Step 2: Generate documentation
        prd_content = self.generator.generate_prd(project_data)
        readme_content = self.generator.generate_readme(project_data)

        # Verify documentation was generated
        self.assertIsInstance(prd_content, str)
        self.assertIsInstance(readme_content, str)
        self.assertGreater(len(prd_content), 1000)
        self.assertGreater(len(readme_content), 500)

        # Step 3: Create a mock codebase for analysis
        folder_contents = {
            "files": [
                "web_app/main.py",
                "web_app/app_analyzer.py",
                "web_app/content_generator.py",
                "static/app.js",
                "static/style.css",
                "templates/index.html",
                "tests/test_main.py",
                "tests/test_analyzer.py",
                "requirements.txt",
                "Dockerfile",
                "docker-compose.yml",
                "README.md",
                ".github/workflows/ci.yml",
            ],
            "directories": [
                "web_app",
                "static",
                "templates",
                "tests",
                ".github/workflows",
            ],
            "file_contents": {
                "web_app/main.py": """
from fastapi import FastAPI, HTTPException
from fastapi.security import HTTPBearer
import logging
import hashlib

app = FastAPI()
security = HTTPBearer()
logger = logging.getLogger(__name__)

@app.get("/")
async def root():
    try:
        return {"message": "Hello World", "status": "ok"}
    except Exception as e:
        logger.error(f"Error in root endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/validate")
async def validate_data(data: dict):
    try:
        # Input validation
        if not data or 'content' not in data:
            raise HTTPException(status_code=400, detail="Invalid input")
        
        # Hash sensitive data
        content_hash = hashlib.sha256(data['content'].encode()).hexdigest()
        
        return {"hash": content_hash, "status": "validated"}
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=500, detail="Validation failed")
""",
                "requirements.txt": """
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
pytest==7.4.3
pytest-cov==4.1.0
""",
                "tests/test_main.py": """
import unittest
from fastapi.testclient import TestClient
from web_app.main import app

class TestMain(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
    
    def test_validate_endpoint(self):
        response = self.client.post("/validate", json={"content": "test"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("hash", response.json())
""",
                "README.md": """
# Integration Test Project

A comprehensive test of the entire system with proper documentation,
testing, security measures, and modern development practices.

## Features
- FastAPI backend with security
- Comprehensive testing
- Docker containerization
- CI/CD pipeline
- Input validation and error handling

## Installation
```bash
pip install -r requirements.txt
```

## Testing
```bash
python -m pytest tests/
```
""",
                "Dockerfile": """
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "web_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
                ".github/workflows/ci.yml": """
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: python -m pytest tests/ --cov=web_app
""",
            },
        }

        # Step 4: Analyze the codebase
        analysis = self.analyzer.analyze_folder_contents(folder_contents)

        # Verify analysis completed successfully
        self.assertIsInstance(analysis, dict)
        self.assertIn("project_structure", analysis)
        self.assertIn("detected_technologies", analysis)
        self.assertIn("security_analysis", analysis)
        self.assertIn("quality_assessment", analysis)
        self.assertIn("architecture_insights", analysis)

        # Step 5: Verify high-quality scores
        security_score = analysis["security_analysis"]["security_score"]
        quality_score = analysis["quality_assessment"]["quality_score"]
        architecture_score = analysis["architecture_insights"]["architectural_score"]

        # Should achieve high scores due to comprehensive setup
        self.assertGreaterEqual(
            security_score, 90, f"Security score {security_score} should be >= 90"
        )
        self.assertGreaterEqual(quality_score, 90, f"Quality score {quality_score} should be >= 90")
        self.assertGreaterEqual(
            architecture_score,
            80,
            f"Architecture score {architecture_score} should be >= 80",
        )

        # Step 6: Verify specific quality indicators were detected
        quality_practices = analysis["quality_assessment"]["implemented_practices"]
        self.assertIn("testing", quality_practices, "Testing should be detected")
        self.assertIn("documentation", quality_practices, "Documentation should be detected")
        self.assertIn("ci_cd", quality_practices, "CI/CD should be detected")
        self.assertIn("error_handling", quality_practices, "Error handling should be detected")

        # Step 7: Verify security features were detected
        security_features = analysis["security_analysis"]["implemented_features"]
        self.assertIn("authentication", security_features, "Authentication should be detected")
        self.assertIn("validation", security_features, "Input validation should be detected")
        self.assertIn("encryption", security_features, "Encryption/hashing should be detected")

        # Step 8: Verify technology detection
        technologies = analysis["detected_technologies"]
        self.assertIn("backend", technologies, "Backend technology should be detected")
        self.assertIn("python", technologies.get("backend", []), "Python should be detected")
        self.assertIn("devops", technologies, "DevOps technology should be detected")
        self.assertIn("docker", technologies.get("devops", []), "Docker should be detected")

    def test_documentation_and_analysis_consistency(self):
        """Test that documentation generation and analysis are consistent"""

        # Generate documentation for a project
        project_data = {
            "project": "Consistency Test",
            "description": "Testing consistency between docs and analysis",
            "components": ["frontend", "backend", "database"],
            "docType": "readme",
            "focusArea": "technical",
            "customAnswers": {},
        }

        readme_content = self.generator.generate_readme(project_data)

        # Create a project structure that matches the documentation
        folder_contents = {
            "files": ["README.md", "main.py", "requirements.txt"],
            "directories": ["src"],
            "file_contents": {
                "README.md": readme_content,
                "main.py": "print('Hello World')",
                "requirements.txt": "fastapi==0.104.1",
            },
        }

        # Analyze the project
        analysis = self.analyzer.analyze_folder_contents(folder_contents)

        # Verify that documentation is detected
        quality_practices = analysis["quality_assessment"]["implemented_practices"]
        self.assertIn("documentation", quality_practices)

        # Verify that the project name appears in both
        self.assertIn("Consistency Test", readme_content)

    def test_system_resilience(self):
        """Test system resilience with edge cases"""

        # Test with minimal project data
        minimal_data = {
            "project": "Minimal",
            "description": "Minimal test",
            "components": ["frontend"],
            "docType": "readme",
            "focusArea": "technical",
            "customAnswers": {},
        }

        # Should not crash
        try:
            readme = self.generator.generate_readme(minimal_data)
            self.assertIsInstance(readme, str)
            self.assertGreater(len(readme), 0)
        except Exception as e:
            self.fail(f"System should handle minimal data: {e}")

        # Test with empty folder contents
        empty_contents = {"files": [], "directories": [], "file_contents": {}}

        # Should not crash
        try:
            analysis = self.analyzer.analyze_folder_contents(empty_contents)
            self.assertIsInstance(analysis, dict)
        except Exception as e:
            self.fail(f"System should handle empty contents: {e}")


class TestSystemPerformance(unittest.TestCase):
    """Performance tests for the system"""

    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = ApplicationAnalyzer()
        self.generator = ContentGenerator()

    def test_large_project_analysis(self):
        """Test analysis of a large project structure"""

        # Create a large project structure
        large_contents = {
            "files": [f"src/module_{i}.py" for i in range(100)]
            + [f"tests/test_module_{i}.py" for i in range(50)]
            + ["README.md", "requirements.txt", "Dockerfile"],
            "directories": ["src", "tests", "docs", "config"],
            "file_contents": {
                "README.md": "# Large Project\nThis is a large test project.",
                "requirements.txt": "fastapi==0.104.1\npytest==7.4.3",
                "src/module_0.py": "def hello(): return 'world'",
                "tests/test_module_0.py": "import unittest\nclass TestModule(unittest.TestCase): pass",
            },
        }

        # Analysis should complete in reasonable time
        import time

        start_time = time.time()

        analysis = self.analyzer.analyze_folder_contents(large_contents)

        end_time = time.time()
        analysis_time = end_time - start_time

        # Should complete within 5 seconds
        self.assertLess(analysis_time, 5.0, f"Analysis took {analysis_time:.2f}s, should be < 5s")

        # Should still produce valid results
        self.assertIsInstance(analysis, dict)
        self.assertIn("quality_assessment", analysis)

        # Should detect testing despite large size
        quality_practices = analysis["quality_assessment"]["implemented_practices"]
        self.assertIn("testing", quality_practices)


if __name__ == "__main__":
    # Run the integration tests
    unittest.main(verbosity=2)

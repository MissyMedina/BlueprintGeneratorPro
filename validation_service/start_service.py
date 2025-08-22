#!/usr/bin/env python3
"""
Startup script for the Project Validation Service
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import requests


def check_dependencies():
    """Check if all dependencies are installed"""
    print("🔍 Checking dependencies...")

    try:
        import fastapi
        import requests
        import uvicorn

        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies:")
        print("  pip install -r requirements.txt")
        return False


def check_analyzer():
    """Check if the analyzer module is available"""
    print("🔍 Checking analyzer module...")

    # Add parent web_app directory to path
    web_app_path = Path(__file__).parent.parent / "web_app"
    if web_app_path.exists():
        sys.path.insert(0, str(web_app_path))

        try:
            from app_analyzer import app_analyzer

            print("✅ Analyzer module is available")
            return True
        except ImportError as e:
            print(f"❌ Cannot import analyzer: {e}")
            print("Please ensure web_app/app_analyzer.py exists")
            return False
    else:
        print(f"❌ Web app directory not found: {web_app_path}")
        return False


def start_service():
    """Start the validation service"""
    print("🚀 Starting Project Validation Service...")

    try:
        # Start the service
        process = subprocess.Popen(
            [sys.executable, "main.py"], cwd=Path(__file__).parent
        )

        # Wait a moment for startup
        time.sleep(3)

        # Check if service is running
        try:
            response = requests.get("http://localhost:8002/", timeout=5)
            if response.status_code == 200:
                service_info = response.json()
                print(f"✅ Service started successfully!")
                print(f"   Service: {service_info['service']}")
                print(f"   Version: {service_info['version']}")
                print(f"   Status: {service_info['status']}")
                print(f"   URL: http://localhost:8002")
                print(f"   Docs: http://localhost:8002/docs")
                return process
            else:
                print(f"❌ Service responded with status {response.status_code}")
                return None
        except requests.RequestException:
            print("❌ Service is not responding")
            return None

    except Exception as e:
        print(f"❌ Failed to start service: {e}")
        return None


def run_example_validation():
    """Run a quick example validation"""
    print("\n🧪 Running example validation...")

    try:
        from client_sdk import ValidationClient

        client = ValidationClient()

        # Validate the parent project
        project_path = Path(__file__).parent.parent

        print(f"Validating project: {project_path.name}")

        results = client.validate_project_folder(
            folder_path=str(project_path),
            project_name="PRD_README_Generator_Test",
            validation_profile="comprehensive",
        )

        print(f"✅ Example validation completed!")
        print(f"   Security Score: {results['scores']['security']}/100")
        print(f"   Quality Score: {results['scores']['quality']}/100")
        print(f"   Architecture Score: {results['scores']['architecture']}/100")

        if results["recommendations"]:
            print(f"   Top Recommendation: {results['recommendations'][0]}")

        return True

    except Exception as e:
        print(f"❌ Example validation failed: {e}")
        return False


def show_usage_examples():
    """Show usage examples"""
    print("\n📖 Usage Examples:")
    print("=" * 50)

    print("\n🐍 Python SDK:")
    print(
        """
from client_sdk import ValidationClient, validate_project

# Quick validation
results = validate_project("/path/to/project")
print(f"Security: {results['scores']['security']}/100")

# Advanced usage
client = ValidationClient()
results = client.validate_project_folder(
    folder_path="/path/to/project",
    project_name="MyProject"
)
"""
    )

    print("\n🌐 REST API:")
    print(
        """
# Health check
curl http://localhost:8002/

# Upload validation
curl -X POST "http://localhost:8002/validate/upload" \\
  -F "file=@project.zip" \\
  -F "project_name=MyProject"

# Git repository validation
curl -X POST "http://localhost:8002/validate/git" \\
  -H "Content-Type: application/json" \\
  -d '{"git_url": "https://github.com/user/repo.git"}'
"""
    )

    print("\n📊 Check results:")
    print(
        """
# Get status
curl http://localhost:8002/validate/{validation_id}/status

# Get results
curl http://localhost:8002/validate/{validation_id}/results

# Download report
curl http://localhost:8002/validate/{validation_id}/report/download
"""
    )


def main():
    """Main startup function"""
    print("🚀 Project Validation Service Startup")
    print("=" * 60)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Check analyzer
    if not check_analyzer():
        sys.exit(1)

    # Start service
    process = start_service()
    if not process:
        sys.exit(1)

    # Run example
    example_success = run_example_validation()

    # Show usage examples
    show_usage_examples()

    print("\n🎉 Service is ready!")
    print("=" * 60)
    print("📖 Interactive API docs: http://localhost:8002/docs")
    print("🔍 Service health: http://localhost:8002/")
    print("📊 Run examples: python examples/validate_examples.py")
    print("\n💡 Press Ctrl+C to stop the service")

    try:
        # Keep the service running
        process.wait()
    except KeyboardInterrupt:
        print("\n\n👋 Stopping service...")
        process.terminate()
        process.wait()
        print("✅ Service stopped")


if __name__ == "__main__":
    main()

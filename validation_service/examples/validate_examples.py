#!/usr/bin/env python3
"""
Example usage of the Project Validation Service
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import json

from client_sdk import ValidationClient, validate_git_repo, validate_project


def example_validate_local_project():
    """Example: Validate a local project folder"""
    print("🔍 Example 1: Validating Local Project Folder")
    print("=" * 50)

    client = ValidationClient()

    # Validate the current project
    project_path = "../.."  # Go up to the main project directory

    try:
        results = client.validate_project_folder(
            folder_path=project_path,
            project_name="PRD_README_Generator",
            validation_profile="comprehensive",
        )

        print(f"✅ Validation completed!")
        print(f"Project: {results['project_name']}")
        print(f"Validation ID: {results['validation_id']}")
        print(f"Timestamp: {results['timestamp']}")

        print(f"\n📊 Scores:")
        scores = results["scores"]
        print(f"  Security: {scores['security']}/100")
        print(f"  Quality: {scores['quality']}/100")
        print(f"  Architecture: {scores['architecture']}/100")

        avg_score = sum(scores.values()) / len(scores)
        print(f"  Average: {avg_score:.1f}/100")

        print(f"\n💡 Top Recommendations:")
        for i, rec in enumerate(results["recommendations"][:5], 1):
            print(f"  {i}. {rec}")

        # Download detailed report
        report_path = client.download_report(results["validation_id"])
        print(f"\n📄 Detailed report saved to: {report_path}")

    except Exception as e:
        print(f"❌ Validation failed: {e}")


def example_validate_git_repository():
    """Example: Validate a public Git repository"""
    print("\n🔍 Example 2: Validating Git Repository")
    print("=" * 50)

    # Example with a popular open-source project
    git_url = "https://github.com/fastapi/fastapi.git"

    try:
        results = validate_git_repo(
            git_url=git_url, project_name="FastAPI", branch="master"
        )

        print(f"✅ Validation completed!")
        print(f"Repository: {git_url}")
        print(f"Project: {results['project_name']}")

        print(f"\n📊 Scores:")
        scores = results["scores"]
        print(f"  Security: {scores['security']}/100")
        print(f"  Quality: {scores['quality']}/100")
        print(f"  Architecture: {scores['architecture']}/100")

        print(f"\n🏗️ Detected Technologies:")
        analysis = results["analysis"]
        tech = analysis.get("detected_technologies", {})
        for category, technologies in tech.items():
            if technologies:
                print(f"  {category.title()}: {', '.join(technologies)}")

    except Exception as e:
        print(f"❌ Validation failed: {e}")


def example_batch_validation():
    """Example: Batch validate multiple projects"""
    print("\n🔍 Example 3: Batch Validation")
    print("=" * 50)

    client = ValidationClient()

    # List of projects to validate
    projects = [
        {"path": "../..", "name": "PRD_README_Generator"},
        # Add more projects here
    ]

    results = []

    for project in projects:
        try:
            print(f"Validating {project['name']}...")

            result = client.validate_project_folder(
                folder_path=project["path"],
                project_name=project["name"],
                wait_for_completion=True,
            )

            results.append(
                {
                    "name": project["name"],
                    "scores": result["scores"],
                    "status": "success",
                }
            )

        except Exception as e:
            results.append(
                {"name": project["name"], "error": str(e), "status": "failed"}
            )

    # Summary report
    print(f"\n📊 Batch Validation Summary:")
    print("-" * 30)

    for result in results:
        if result["status"] == "success":
            scores = result["scores"]
            avg = sum(scores.values()) / len(scores)
            print(
                f"{result['name']}: {avg:.1f}/100 (S:{scores['security']} Q:{scores['quality']} A:{scores['architecture']})"
            )
        else:
            print(f"{result['name']}: FAILED - {result['error']}")


def example_async_validation():
    """Example: Asynchronous validation with status polling"""
    print("\n🔍 Example 4: Asynchronous Validation")
    print("=" * 50)

    client = ValidationClient()

    try:
        # Start validation without waiting
        result = client.validate_project_folder(
            folder_path="../..",
            project_name="PRD_README_Generator_Async",
            wait_for_completion=False,
        )

        validation_id = result["validation_id"]
        print(f"✅ Validation started: {validation_id}")

        # Poll for status
        import time

        while True:
            status = client.get_validation_status(validation_id)
            print(
                f"Status: {status['status']} - {status['progress']}% - {status['message']}"
            )

            if status["status"] in ["completed", "failed"]:
                break

            time.sleep(2)

        if status["status"] == "completed":
            results = client.get_validation_results(validation_id)
            print(f"\n✅ Validation completed!")
            print(f"Scores: {results['scores']}")
        else:
            print(f"❌ Validation failed: {status['message']}")

    except Exception as e:
        print(f"❌ Error: {e}")


def example_custom_validation_profiles():
    """Example: Using different validation profiles"""
    print("\n🔍 Example 5: Custom Validation Profiles")
    print("=" * 50)

    client = ValidationClient()

    profiles = ["comprehensive", "security-focused", "quality-focused"]

    for profile in profiles:
        try:
            print(f"\nValidating with profile: {profile}")

            result = client.validate_project_folder(
                folder_path="../..",
                project_name=f"PRD_README_Generator_{profile}",
                validation_profile=profile,
            )

            scores = result["scores"]
            print(f"  Security: {scores['security']}/100")
            print(f"  Quality: {scores['quality']}/100")
            print(f"  Architecture: {scores['architecture']}/100")

        except Exception as e:
            print(f"  ❌ Failed: {e}")


if __name__ == "__main__":
    print("🚀 Project Validation Service Examples")
    print("=" * 60)

    # Check if service is running
    try:
        client = ValidationClient()
        health = client.health_check()
        print(f"✅ Service is running: {health['service']} v{health['version']}")
    except Exception as e:
        print(f"❌ Service not available: {e}")
        print("Please start the validation service first:")
        print("  cd validation_service")
        print("  python main.py")
        sys.exit(1)

    # Run examples
    try:
        example_validate_local_project()
        # example_validate_git_repository()  # Uncomment to test Git validation
        # example_batch_validation()         # Uncomment to test batch validation
        # example_async_validation()         # Uncomment to test async validation
        # example_custom_validation_profiles()  # Uncomment to test profiles

    except KeyboardInterrupt:
        print("\n\n👋 Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback

        traceback.print_exc()

    print("\n✨ Examples completed!")

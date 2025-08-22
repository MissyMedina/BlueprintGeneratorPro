#!/usr/bin/env python3
"""
Performance testing with Locust for Guidance Blueprint Kit Pro
"""

import json
import random

from locust import HttpUser, between, task


class BlueprintProUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests

    def on_start(self):
        """Called when a user starts"""
        # Load the main page
        self.client.get("/")

    @task(3)
    def load_homepage(self):
        """Load the main homepage"""
        self.client.get("/")

    @task(2)
    def get_profiles(self):
        """Get available profiles"""
        self.client.get("/api/profiles")

    @task(1)
    def generate_document(self):
        """Generate a document (most resource-intensive)"""

        # Sample request data
        request_data = {
            "project": f"Test Project {random.randint(1, 1000)}",
            "modules": ["claims", "evidence"],
            "claims_scope": "app",
            "profile": "full-eval",
            "tags": {
                "doc_type": random.choice(["prd", "readme", "mvp"]),
                "project_type": random.choice(["web-app", "mobile-app", "api"]),
                "description": "Performance test project for load testing",
                "target_audience": "Developers and QA engineers",
                "key_features": "High performance, scalability, reliability",
            },
            "evidence_data": [
                {
                    "claim": "Performance testing implemented",
                    "evidence": "Locust performance tests configured",
                    "status": "Implemented",
                    "notes": "Load testing with multiple concurrent users",
                }
            ],
            "repo_scan": False,
        }

        # Make the request
        with self.client.post(
            "/api/generate",
            json=request_data,
            headers={"Content-Type": "application/json"},
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get("success"):
                        response.success()
                    else:
                        response.failure(
                            f"Generation failed: {result.get('error', 'Unknown error')}"
                        )
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            elif response.status_code == 429:
                # Rate limiting is expected
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(1)
    def upload_repo_simulation(self):
        """Simulate repository upload (without actual file)"""

        # This would normally upload a file, but for performance testing
        # we'll just test the endpoint availability
        response = self.client.post(
            "/api/upload-repo",
            files={"file": ("test.txt", "print('hello world')", "text/plain")},
            catch_response=True,
        )

        # We expect this to fail without proper file, but endpoint should respond
        if response.status_code in [400, 422]:  # Expected validation errors
            response.success()
        elif response.status_code == 429:  # Rate limiting
            response.success()


class AdminUser(HttpUser):
    """Simulates admin/power user behavior"""

    wait_time = between(0.5, 2)
    weight = 1  # Lower weight = fewer admin users

    @task
    def rapid_profile_checks(self):
        """Admin checking profiles rapidly"""
        self.client.get("/api/profiles")

    @task
    def bulk_document_generation(self):
        """Generate multiple documents quickly"""
        for i in range(3):
            request_data = {
                "project": f"Bulk Test {i}",
                "modules": ["claims"],
                "claims_scope": "component",
                "profile": "sec-audit",
                "tags": {
                    "doc_type": "prd",
                    "project_type": "api",
                    "description": f"Bulk generation test {i}",
                },
            }

            self.client.post("/api/generate", json=request_data)


class MobileUser(HttpUser):
    """Simulates mobile user behavior"""

    wait_time = between(2, 5)  # Mobile users typically slower
    weight = 2

    def on_start(self):
        # Mobile users might have slower initial load
        self.client.get("/", headers={"User-Agent": "Mobile"})

    @task(5)
    def mobile_homepage_browsing(self):
        """Mobile users browsing the homepage"""
        self.client.get("/")

    @task(1)
    def mobile_document_generation(self):
        """Mobile users generating simpler documents"""
        request_data = {
            "project": "Mobile Project",
            "modules": ["claims"],
            "claims_scope": "app",
            "profile": "full-eval",
            "tags": {
                "doc_type": "readme",
                "project_type": "mobile-app",
                "description": "Mobile-generated project",
            },
        }

        self.client.post("/api/generate", json=request_data)


# Custom load shape for realistic traffic patterns
from locust import LoadTestShape


class StepLoadShape(LoadTestShape):
    """
    A step load shape that increases users in steps
    """

    step_time = 30  # seconds
    step_load = 5  # users per step
    spawn_rate = 2  # users per second
    time_limit = 300  # total test time in seconds

    def tick(self):
        run_time = self.get_run_time()

        if run_time > self.time_limit:
            return None

        current_step = run_time // self.step_time
        return (current_step * self.step_load, self.spawn_rate)


# Usage examples:
# Basic load test: locust --headless --users 10 --spawn-rate 2 --run-time 60s --host http://localhost:8001
# Step load test: locust --headless --run-time 300s --host http://localhost:8001
# Web UI test: locust --host http://localhost:8001

#!/usr/bin/env python3
"""
Project Validation Service
A standalone service that validates any codebase using the same analysis engine
"""

import json
import os
import shutil
import sys
import tempfile
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Add the web_app directory to the path to import our analyzer
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "web_app"))
from app_analyzer import app_analyzer

app = FastAPI(
    title="Project Validation Service",
    description="Professional codebase validation and analysis service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for validation results (use Redis/DB in production)
validation_results = {}


class ValidationRequest(BaseModel):
    project_name: str
    project_type: Optional[str] = None
    validation_profile: Optional[str] = "comprehensive"
    callback_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class ValidationResponse(BaseModel):
    validation_id: str
    status: str
    project_name: str
    scores: Dict[str, int]
    analysis: Dict[str, Any]
    recommendations: List[str]
    timestamp: str
    report_url: Optional[str] = None


class ValidationStatus(BaseModel):
    validation_id: str
    status: str
    progress: int
    message: str
    estimated_completion: Optional[str] = None


@app.get("/")
async def root():
    """Service health check and info"""
    return {
        "service": "Project Validation Service",
        "version": "1.0.0",
        "status": "active",
        "capabilities": [
            "Codebase Analysis",
            "Security Assessment",
            "Quality Evaluation",
            "Architecture Review",
            "Technology Detection",
            "Improvement Recommendations",
        ],
        "supported_formats": [".zip", ".tar.gz", ".tar"],
        "endpoints": {
            "validate_upload": "/validate/upload",
            "validate_folder": "/validate/folder",
            "validate_git": "/validate/git",
            "status": "/validate/{validation_id}/status",
            "results": "/validate/{validation_id}/results",
            "report": "/validate/{validation_id}/report",
        },
    }


@app.post("/validate/upload", response_model=ValidationResponse)
async def validate_uploaded_project(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    project_name: Optional[str] = None,
    validation_profile: str = "comprehensive",
):
    """Validate an uploaded project archive"""

    if not file.filename.endswith((".zip", ".tar.gz", ".tar")):
        raise HTTPException(
            status_code=400, detail="Only ZIP and TAR files are supported"
        )

    validation_id = str(uuid.uuid4())
    project_name = project_name or os.path.splitext(file.filename)[0]

    # Initialize validation status
    validation_results[validation_id] = {
        "status": "processing",
        "progress": 0,
        "project_name": project_name,
        "timestamp": datetime.now().isoformat(),
        "validation_profile": validation_profile,
    }

    # Process in background
    background_tasks.add_task(
        process_uploaded_file, validation_id, file, project_name, validation_profile
    )

    return ValidationResponse(
        validation_id=validation_id,
        status="processing",
        project_name=project_name,
        scores={},
        analysis={},
        recommendations=[],
        timestamp=datetime.now().isoformat(),
    )


@app.post("/validate/folder")
async def validate_folder_contents(
    background_tasks: BackgroundTasks, request: Dict[str, Any]
):
    """Validate folder contents directly"""

    validation_id = str(uuid.uuid4())
    project_name = request.get("project_name", "Local Project")
    folder_contents = request.get("folder_contents", {})
    validation_profile = request.get("validation_profile", "comprehensive")

    if not folder_contents:
        raise HTTPException(status_code=400, detail="No folder contents provided")

    # Initialize validation status
    validation_results[validation_id] = {
        "status": "processing",
        "progress": 0,
        "project_name": project_name,
        "timestamp": datetime.now().isoformat(),
        "validation_profile": validation_profile,
    }

    # Process in background
    background_tasks.add_task(
        process_folder_contents,
        validation_id,
        folder_contents,
        project_name,
        validation_profile,
    )

    return {
        "validation_id": validation_id,
        "status": "processing",
        "message": "Validation started",
        "estimated_completion": "30-60 seconds",
    }


@app.post("/validate/git")
async def validate_git_repository(
    background_tasks: BackgroundTasks,
    git_url: str,
    project_name: Optional[str] = None,
    branch: str = "main",
    validation_profile: str = "comprehensive",
):
    """Validate a Git repository"""

    validation_id = str(uuid.uuid4())
    project_name = project_name or git_url.split("/")[-1].replace(".git", "")

    # Initialize validation status
    validation_results[validation_id] = {
        "status": "processing",
        "progress": 0,
        "project_name": project_name,
        "timestamp": datetime.now().isoformat(),
        "validation_profile": validation_profile,
    }

    # Process in background
    background_tasks.add_task(
        process_git_repository,
        validation_id,
        git_url,
        branch,
        project_name,
        validation_profile,
    )

    return {
        "validation_id": validation_id,
        "status": "processing",
        "message": "Cloning and validating repository",
        "estimated_completion": "1-3 minutes",
    }


@app.get("/validate/{validation_id}/status", response_model=ValidationStatus)
async def get_validation_status(validation_id: str):
    """Get validation status"""

    if validation_id not in validation_results:
        raise HTTPException(status_code=404, detail="Validation not found")

    result = validation_results[validation_id]

    return ValidationStatus(
        validation_id=validation_id,
        status=result["status"],
        progress=result.get("progress", 0),
        message=result.get("message", "Processing..."),
        estimated_completion=result.get("estimated_completion"),
    )


@app.get("/validate/{validation_id}/results", response_model=ValidationResponse)
async def get_validation_results(validation_id: str):
    """Get validation results"""

    if validation_id not in validation_results:
        raise HTTPException(status_code=404, detail="Validation not found")

    result = validation_results[validation_id]

    if result["status"] != "completed":
        raise HTTPException(
            status_code=202, detail=f"Validation still {result['status']}"
        )

    return ValidationResponse(
        validation_id=validation_id,
        status=result["status"],
        project_name=result["project_name"],
        scores=result.get("scores", {}),
        analysis=result.get("analysis", {}),
        recommendations=result.get("recommendations", []),
        timestamp=result["timestamp"],
        report_url=f"/validate/{validation_id}/report",
    )


@app.get("/validate/{validation_id}/report")
async def get_validation_report(validation_id: str):
    """Get detailed validation report"""

    if validation_id not in validation_results:
        raise HTTPException(status_code=404, detail="Validation not found")

    result = validation_results[validation_id]

    if result["status"] != "completed":
        raise HTTPException(
            status_code=202, detail=f"Validation still {result['status']}"
        )

    # Generate comprehensive report
    report = generate_detailed_report(result)

    return JSONResponse(
        content={
            "validation_id": validation_id,
            "report": report,
            "download_url": f"/validate/{validation_id}/report/download",
        }
    )


@app.get("/validate/{validation_id}/report/download")
async def download_validation_report(validation_id: str):
    """Download validation report as markdown file"""

    if validation_id not in validation_results:
        raise HTTPException(status_code=404, detail="Validation not found")

    result = validation_results[validation_id]

    if result["status"] != "completed":
        raise HTTPException(
            status_code=202, detail=f"Validation still {result['status']}"
        )

    # Generate markdown report
    report_content = app_analyzer.generate_analysis_report(
        result["analysis"], result["project_name"]
    )

    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False)
    temp_file.write(report_content)
    temp_file.close()

    return FileResponse(
        temp_file.name,
        media_type="text/markdown",
        filename=f"{result['project_name']}-validation-report.md",
    )


# Background processing functions
async def process_uploaded_file(
    validation_id: str, file: UploadFile, project_name: str, validation_profile: str
):
    """Process uploaded file in background"""
    try:
        # Update progress
        validation_results[validation_id]["progress"] = 10
        validation_results[validation_id]["message"] = "Extracting archive..."

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(file.filename)[1]
        ) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name

        validation_results[validation_id]["progress"] = 30
        validation_results[validation_id]["message"] = "Analyzing codebase..."

        # Analyze the codebase
        analysis = app_analyzer.analyze_codebase(temp_file_path)

        validation_results[validation_id]["progress"] = 80
        validation_results[validation_id]["message"] = "Generating recommendations..."

        # Extract scores and recommendations
        scores = {
            "security": analysis.get("security_analysis", {}).get("security_score", 0),
            "quality": analysis.get("quality_assessment", {}).get("quality_score", 0),
            "architecture": analysis.get("architecture_insights", {}).get(
                "architectural_score", 0
            ),
        }

        recommendations = analysis.get("improvement_suggestions", [])

        # Update final results
        validation_results[validation_id].update(
            {
                "status": "completed",
                "progress": 100,
                "message": "Validation completed successfully",
                "scores": scores,
                "analysis": analysis,
                "recommendations": recommendations,
            }
        )

        # Clean up temporary file
        os.unlink(temp_file_path)

    except Exception as e:
        validation_results[validation_id].update(
            {
                "status": "failed",
                "progress": 0,
                "message": f"Validation failed: {str(e)}",
            }
        )


async def process_folder_contents(
    validation_id: str,
    folder_contents: Dict[str, Any],
    project_name: str,
    validation_profile: str,
):
    """Process folder contents in background"""
    try:
        validation_results[validation_id]["progress"] = 20
        validation_results[validation_id]["message"] = "Analyzing folder structure..."

        # Analyze folder contents
        analysis = app_analyzer.analyze_folder_contents(folder_contents)

        validation_results[validation_id]["progress"] = 80
        validation_results[validation_id]["message"] = "Generating recommendations..."

        # Extract scores and recommendations
        scores = {
            "security": analysis.get("security_analysis", {}).get("security_score", 0),
            "quality": analysis.get("quality_assessment", {}).get("quality_score", 0),
            "architecture": analysis.get("architecture_insights", {}).get(
                "architectural_score", 0
            ),
        }

        recommendations = analysis.get("improvement_suggestions", [])

        # Update final results
        validation_results[validation_id].update(
            {
                "status": "completed",
                "progress": 100,
                "message": "Validation completed successfully",
                "scores": scores,
                "analysis": analysis,
                "recommendations": recommendations,
            }
        )

    except Exception as e:
        validation_results[validation_id].update(
            {
                "status": "failed",
                "progress": 0,
                "message": f"Validation failed: {str(e)}",
            }
        )


async def process_git_repository(
    validation_id: str,
    git_url: str,
    branch: str,
    project_name: str,
    validation_profile: str,
):
    """Process Git repository in background"""
    try:
        import subprocess

        validation_results[validation_id]["progress"] = 10
        validation_results[validation_id]["message"] = "Cloning repository..."

        # Clone repository to temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            clone_path = os.path.join(temp_dir, project_name)

            # Clone the repository
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    branch,
                    git_url,
                    clone_path,
                ],
                check=True,
                capture_output=True,
            )

            validation_results[validation_id]["progress"] = 40
            validation_results[validation_id]["message"] = "Analyzing repository..."

            # Read folder contents
            folder_contents = read_directory_contents(clone_path)

            validation_results[validation_id]["progress"] = 60
            validation_results[validation_id]["message"] = "Running analysis..."

            # Analyze the repository
            analysis = app_analyzer.analyze_folder_contents(folder_contents)

            validation_results[validation_id]["progress"] = 90
            validation_results[validation_id][
                "message"
            ] = "Generating recommendations..."

            # Extract scores and recommendations
            scores = {
                "security": analysis.get("security_analysis", {}).get(
                    "security_score", 0
                ),
                "quality": analysis.get("quality_assessment", {}).get(
                    "quality_score", 0
                ),
                "architecture": analysis.get("architecture_insights", {}).get(
                    "architectural_score", 0
                ),
            }

            recommendations = analysis.get("improvement_suggestions", [])

            # Update final results
            validation_results[validation_id].update(
                {
                    "status": "completed",
                    "progress": 100,
                    "message": "Validation completed successfully",
                    "scores": scores,
                    "analysis": analysis,
                    "recommendations": recommendations,
                }
            )

    except Exception as e:
        validation_results[validation_id].update(
            {
                "status": "failed",
                "progress": 0,
                "message": f"Validation failed: {str(e)}",
            }
        )


def read_directory_contents(directory_path: str) -> Dict[str, Any]:
    """Read directory contents for analysis"""
    contents = {"files": [], "directories": [], "file_contents": {}}

    for root, dirs, files in os.walk(directory_path):
        # Skip common ignore directories
        dirs[:] = [
            d
            for d in dirs
            if d not in [".git", "__pycache__", "node_modules", ".venv", "venv"]
        ]

        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory_path)
            contents["files"].append(relative_path)

            # Read text files (limit size)
            if (
                is_text_file(file) and os.path.getsize(file_path) < 1024 * 1024
            ):  # 1MB limit
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        contents["file_contents"][relative_path] = f.read()
                except:
                    pass  # Skip files that can't be read

        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            relative_path = os.path.relpath(dir_path, directory_path)
            contents["directories"].append(relative_path)

    return contents


def is_text_file(filename: str) -> bool:
    """Check if file is likely a text file"""
    text_extensions = [
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
    ]

    ext = os.path.splitext(filename.lower())[1]
    return (
        ext in text_extensions
        or "makefile" in filename.lower()
        or "dockerfile" in filename.lower()
    )


def generate_detailed_report(result: Dict[str, Any]) -> Dict[str, Any]:
    """Generate detailed validation report"""
    analysis = result.get("analysis", {})

    return {
        "project_name": result["project_name"],
        "validation_id": result.get("validation_id"),
        "timestamp": result["timestamp"],
        "scores": result.get("scores", {}),
        "executive_summary": {
            "overall_grade": calculate_overall_grade(result.get("scores", {})),
            "key_strengths": extract_strengths(analysis),
            "priority_improvements": result.get("recommendations", [])[:5],
            "technology_stack": analysis.get("detected_technologies", {}),
            "project_type": analysis.get("application_type", {}).get(
                "description", "Unknown"
            ),
        },
        "detailed_analysis": analysis,
        "recommendations": {
            "immediate": result.get("recommendations", [])[:3],
            "medium_term": result.get("recommendations", [])[3:6],
            "long_term": result.get("recommendations", [])[6:],
        },
        "compliance_status": {
            "security_compliant": result.get("scores", {}).get("security", 0) >= 80,
            "quality_compliant": result.get("scores", {}).get("quality", 0) >= 80,
            "architecture_compliant": result.get("scores", {}).get("architecture", 0)
            >= 80,
        },
    }


def calculate_overall_grade(scores: Dict[str, int]) -> str:
    """Calculate overall project grade"""
    if not scores:
        return "N/A"

    avg_score = sum(scores.values()) / len(scores)

    if avg_score >= 90:
        return "A+ (Excellent)"
    elif avg_score >= 80:
        return "A (Very Good)"
    elif avg_score >= 70:
        return "B (Good)"
    elif avg_score >= 60:
        return "C (Fair)"
    else:
        return "D (Needs Improvement)"


def extract_strengths(analysis: Dict[str, Any]) -> List[str]:
    """Extract key project strengths"""
    strengths = []

    # Security strengths
    security = analysis.get("security_analysis", {})
    if security.get("security_score", 0) >= 90:
        strengths.append("Excellent security implementation")

    # Quality strengths
    quality = analysis.get("quality_assessment", {})
    if quality.get("quality_score", 0) >= 90:
        strengths.append("High code quality standards")

    # Architecture strengths
    architecture = analysis.get("architecture_insights", {})
    if architecture.get("architectural_score", 0) >= 90:
        strengths.append("Well-structured architecture")

    # Technology strengths
    tech = analysis.get("detected_technologies", {})
    if tech.get("devops"):
        strengths.append("Modern DevOps practices")

    return strengths[:5]  # Limit to top 5 strengths


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)

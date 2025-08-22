#!/usr/bin/env python3
"""
Guidance Blueprint Kit Pro - Web Application
FastAPI backend for the professional documentation generator
"""

import json
import os
import shutil
import sys
import tempfile
import time
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import (
    BackgroundTasks,
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Add the GuidanceBlueprintKit-Pro directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "GuidanceBlueprintKit-Pro"))

# Import the core blueprint functionality
try:
    from blueprint_pro import (
        assemble,
        collect_repo_findings,
        load_profiles,
        parse_tags,
        read_evidence_csv,
    )
    from docscore import score as calculate_score
except ImportError as e:
    print(f"Error importing blueprint modules: {e}")
    print("Make sure the GuidanceBlueprintKit-Pro directory is accessible")
    sys.exit(1)

from app_analyzer import app_analyzer
from content_generator import content_generator
from export_utils import document_exporter
from monitoring import HealthChecker, monitor, structured_logger, track_performance
from standards_checker import standards_checker

# Rate limiting setup
rate_limit_storage = defaultdict(list)


def custom_rate_limiter(request: Request, calls: int = 10, period: int = 60):
    """Custom rate limiter implementation"""
    client_ip = request.client.host
    current_time = time.time()

    # Clean old requests
    rate_limit_storage[client_ip] = [
        req_time for req_time in rate_limit_storage[client_ip] if current_time - req_time < period
    ]

    # Check if limit exceeded
    if len(rate_limit_storage[client_ip]) >= calls:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {calls} requests per {period} seconds",
        )

    # Add current request
    rate_limit_storage[client_ip].append(current_time)


app = FastAPI(
    title="Blueprint Generator Pro",
    description="Professional documentation generator for PRDs, READMEs, MVPs, and validation documents",
    version="1.0.0",
)

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "*.localhost"])

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001", "http://127.0.0.1:8001"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com; "
        "font-src 'self' https://cdnjs.cloudflare.com; "
        "img-src 'self' data:; "
        "connect-src 'self' http://localhost:8002;"
    )

    return response


# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Pydantic models for API
class GenerationRequest(BaseModel):
    project: str = Field(..., description="Project name")
    modules: List[str] = Field(..., description="List of modules to include")
    claims_scope: str = Field(default="app", description="Scope for claims module")
    profile: Optional[str] = Field(None, description="Profile name to use")
    tags: Optional[Dict[str, str]] = Field(None, description="Custom tags")
    evidence_data: Optional[List[Dict[str, str]]] = Field(None, description="Evidence rows")
    repo_scan: bool = Field(False, description="Whether to scan uploaded repository")
    skip_categories: Optional[List[str]] = Field(
        None, description="Categories to skip in repo scan"
    )
    max_findings: int = Field(50, description="Maximum findings from repo scan")


class GenerationResponse(BaseModel):
    success: bool
    document_id: str
    markdown_content: str
    quality_score: Dict[str, Any]
    filename: str


class ProfilesResponse(BaseModel):
    profiles: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    version: str


# In-memory storage for generated documents (use database in production)
generated_documents = {}


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main application page"""
    with open("templates/index.html", "r") as f:
        return f.read()


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", version="1.0.0")


@app.get("/api/health/detailed")
async def detailed_health_check():
    """Detailed health check with system metrics"""
    health = HealthChecker.check_system_health()
    dependencies = HealthChecker.check_dependencies()

    return {
        "status": (
            "healthy"
            if health["status"] == "healthy" and dependencies["status"] == "healthy"
            else "unhealthy"
        ),
        "system": health,
        "dependencies": dependencies,
        "performance": monitor.get_stats(),
    }


@app.get("/api/metrics")
async def get_metrics():
    """Get application performance metrics"""
    return monitor.get_stats()


@app.get("/api/profiles", response_model=ProfilesResponse)
async def get_profiles():
    """Get available profiles"""
    try:
        profiles = load_profiles()
        return ProfilesResponse(profiles=profiles)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading profiles: {str(e)}")


@app.get("/api/standards")
async def get_standards():
    """Get current compliance standards"""
    try:
        standards = await standards_checker.check_all_standards()
        return {
            "success": True,
            "standards": {
                name: {
                    "name": std.name,
                    "version": std.version,
                    "status": std.status,
                    "last_updated": std.last_updated.isoformat(),
                    "description": std.description,
                    "severity": std.severity,
                    "compliance_items": std.compliance_items,
                }
                for name, std in standards.items()
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking standards: {str(e)}")


@app.get("/api/standards/checklist/{scope}")
async def get_standards_checklist(scope: str):
    """Get compliance checklist for specific scope"""
    try:
        standards = await standards_checker.check_all_standards()
        checklist = standards_checker.generate_compliance_checklist(standards, scope)
        return {
            "success": True,
            "scope": scope,
            "checklist": checklist,
            "count": len(checklist),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating checklist: {str(e)}")


@app.post("/api/generate", response_model=GenerationResponse)
async def generate_document(request: GenerationRequest, http_request: Request):
    """Generate a documentation file based on the request"""
    # Apply rate limiting
    custom_rate_limiter(http_request, calls=5, period=60)  # 5 requests per minute

    try:
        # Load profiles if profile is specified
        profiles = load_profiles()
        modules = request.modules
        claims_scope = request.claims_scope

        if request.profile:
            if request.profile not in profiles:
                raise HTTPException(status_code=400, detail=f"Unknown profile: {request.profile}")
            profile_data = profiles[request.profile]
            modules = profile_data["modules"]
            claims_scope = profile_data["claims_scope"]

        if not modules:
            raise HTTPException(status_code=400, detail="No modules specified")

        # Prepare evidence rows
        evidence_rows = request.evidence_data or []

        # Add standards-based evidence if claims module is included
        if "claims" in modules:
            try:
                standards = await standards_checker.check_all_standards()
                standards_evidence = standards_checker.generate_compliance_checklist(
                    standards, claims_scope
                )
                evidence_rows.extend(
                    standards_evidence[:10]
                )  # Limit to 10 items to avoid overwhelming
            except Exception as e:
                print(f"Warning: Could not load standards evidence: {e}")

        # Extract intelligent context from tags
        doc_type = request.tags.get("doc_type", "prd") if request.tags else "prd"
        project_type = request.tags.get("project_type", "web-app") if request.tags else "web-app"
        description = request.tags.get("description", "") if request.tags else ""

        # Extract custom answers from tags
        custom_answers = {}
        if request.tags:
            for key, value in request.tags.items():
                if key not in ["doc_type", "project_type", "description"]:
                    custom_answers[key] = value

        # Generate intelligent, contextual content
        if doc_type == "prd":
            markdown_content = content_generator.generate_prd_content(
                project_name=request.project,
                project_type=project_type,
                description=description,
                custom_answers=custom_answers,
                focus_area=claims_scope,
            )
        elif doc_type == "readme":
            markdown_content = content_generator.generate_readme_content(
                project_name=request.project,
                project_type=project_type,
                description=description,
                custom_answers=custom_answers,
            )
        else:
            # Fallback to original system for other doc types
            markdown_content = assemble(
                project=request.project,
                modules=modules,
                claims_scope=claims_scope,
                evidence_rows=evidence_rows,
                tags=request.tags,
            )

        # Calculate quality score
        quality_score = calculate_score(markdown_content)

        # Generate unique document ID and filename
        doc_id = str(uuid.uuid4())
        safe_project = (
            "".join(ch for ch in request.project if ch.isalnum() or ch in ("-", "_")).strip()
            or "Project"
        )
        filename = f"{safe_project}-{'-'.join(modules)}.md"

        # Store the document (in production, use a database)
        generated_documents[doc_id] = {
            "content": markdown_content,
            "filename": filename,
            "quality_score": quality_score,
        }

        return GenerationResponse(
            success=True,
            document_id=doc_id,
            markdown_content=markdown_content,
            quality_score=quality_score,
            filename=filename,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating document: {str(e)}")


@app.get("/api/document/{document_id}")
async def get_document(document_id: str):
    """Retrieve a generated document"""
    if document_id not in generated_documents:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = generated_documents[document_id]

    # Create a temporary file to return
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as temp_file:
        temp_file.write(doc["content"])
        temp_file_path = temp_file.name

    return FileResponse(path=temp_file_path, filename=doc["filename"], media_type="text/markdown")


@app.get("/api/export/{document_id}/{export_format}")
async def export_document(document_id: str, export_format: str):
    """Export document in specified format"""
    if document_id not in generated_documents:
        raise HTTPException(status_code=404, detail="Document not found")

    if export_format not in document_exporter.supported_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Supported: {document_exporter.supported_formats}",
        )

    doc = generated_documents[document_id]
    metadata = {
        "project": "Unknown",  # Extract from content if needed
        "generated": datetime.now().isoformat(),
        "modules": "unknown",
        "claims_scope": "app",
        "quality_score": doc["quality_score"],
    }

    try:
        if export_format == "md":
            content = document_exporter.export_markdown(doc["content"], metadata)
            media_type = "text/markdown"
            filename = doc["filename"]
        elif export_format == "html":
            content = document_exporter.export_html(doc["content"], metadata)
            media_type = "text/html"
            filename = doc["filename"].replace(".md", ".html")
        elif export_format == "json":
            content = document_exporter.export_json(doc["content"], metadata)
            media_type = "application/json"
            filename = doc["filename"].replace(".md", ".json")
        elif export_format == "txt":
            content = document_exporter.export_text(doc["content"], metadata)
            media_type = "text/plain"
            filename = doc["filename"].replace(".md", ".txt")
        else:
            raise HTTPException(status_code=400, detail="Invalid format")

        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=f".{export_format}", delete=False
        ) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        return FileResponse(path=temp_file_path, filename=filename, media_type=media_type)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting document: {str(e)}")


@app.get("/api/share/{document_id}")
async def share_document(document_id: str):
    """Get shareable link and QR code for document"""
    if document_id not in generated_documents:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        base_url = "http://localhost:8000"  # In production, use actual domain
        share_url = document_exporter.create_shareable_link(document_id, base_url)
        qr_code = document_exporter.generate_qr_code(share_url)

        return {
            "success": True,
            "share_url": share_url,
            "qr_code": qr_code,
            "document_id": document_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating share link: {str(e)}")


@app.post("/api/analyze-app")
async def analyze_application(file: UploadFile = File(...)):
    """Analyze an existing application codebase from uploaded file"""
    if not file.filename.endswith((".zip", ".tar.gz", ".tar")):
        raise HTTPException(status_code=400, detail="Only ZIP and TAR files are supported")

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(file.filename)[1]
        ) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name

        try:
            # Analyze the codebase
            analysis = app_analyzer.analyze_codebase(temp_file_path)

            if "error" in analysis:
                raise HTTPException(status_code=400, detail=analysis["error"])

            # Generate comprehensive report
            project_name = os.path.splitext(file.filename)[0]
            analysis_report = app_analyzer.generate_analysis_report(analysis, project_name)

            return {
                "success": True,
                "analysis": analysis,
                "report": analysis_report,
                "filename": f"{project_name}-analysis.md",
            }

        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing application: {str(e)}")


@app.post("/api/analyze-local-folder")
async def analyze_local_folder(request: dict):
    """Analyze a local folder's contents"""
    try:
        folder_name = request.get("folder_name", "Local Project")
        folder_contents = request.get("folder_contents", {})

        if not folder_contents:
            raise HTTPException(status_code=400, detail="No folder contents provided")

        # Analyze the folder contents directly
        analysis = app_analyzer.analyze_folder_contents(folder_contents)

        if "error" in analysis:
            raise HTTPException(status_code=400, detail=analysis["error"])

        # Generate comprehensive report
        analysis_report = app_analyzer.generate_analysis_report(analysis, folder_name)

        return {
            "success": True,
            "analysis": analysis,
            "report": analysis_report,
            "filename": f"{folder_name}-analysis.md",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing local folder: {str(e)}")


@app.post("/api/upload-repo")
async def upload_repository(file: UploadFile = File(...)):
    """Upload and analyze a repository for evidence extraction"""
    if not file.filename.endswith((".zip", ".tar.gz", ".tar")):
        raise HTTPException(status_code=400, detail="Only ZIP and TAR files are supported")

    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded file
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Extract archive (simplified - add proper extraction logic)
            extract_dir = os.path.join(temp_dir, "extracted")
            os.makedirs(extract_dir)

            # For now, return a placeholder response
            # In production, implement proper archive extraction and scanning
            findings = [
                {
                    "claim": "Repository uploaded successfully",
                    "evidence": f"File: {file.filename}",
                    "status": "✅",
                    "notes": "Ready for analysis",
                }
            ]

            return {"success": True, "findings": findings}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing repository: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)

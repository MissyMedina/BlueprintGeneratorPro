# 🔌 API Reference

**Blueprint Generator Pro - Complete API Documentation**

This document provides comprehensive API reference for integrating Blueprint Generator Pro into your applications and workflows.

## 🌐 **Base URLs**

- **Document Generator**: `http://localhost:8001`
- **Validation Service**: `http://localhost:8002`
- **Production**: `https://api.blueprintgeneratorpro.com`

## 🔐 **Authentication**

### **API Key Authentication** (Enterprise)
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     https://api.blueprintgeneratorpro.com/api/generate
```

### **Rate Limiting**
- **General Endpoints**: 10 requests per minute
- **Generation Endpoints**: 5 requests per minute
- **Validation Endpoints**: 3 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 1640995200
```

## 📝 **Document Generator API**

### **Health Check**
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### **Get Available Profiles**
```http
GET /api/profiles
```

**Response:**
```json
{
  "profiles": {
    "full-eval": {
      "name": "Full Evaluation",
      "description": "Comprehensive analysis with all modules",
      "modules": ["claims", "evidence"],
      "claims_scope": "app"
    },
    "sec-audit": {
      "name": "Security Audit",
      "description": "Security-focused evaluation",
      "modules": ["claims"],
      "claims_scope": "security"
    }
  }
}
```

### **Generate Document**
```http
POST /api/generate
Content-Type: application/json
```

**Request Body:**
```json
{
  "project": "My Awesome Project",
  "modules": ["claims", "evidence"],
  "claims_scope": "app",
  "profile": "full-eval",
  "tags": {
    "doc_type": "prd",
    "project_type": "web-app",
    "description": "A revolutionary web application",
    "target_audience": "Developers and product managers",
    "key_features": "Real-time collaboration, AI-powered insights",
    "success_metrics": "User engagement, conversion rates"
  },
  "evidence_data": [
    {
      "claim": "User authentication implemented",
      "evidence": "JWT tokens with refresh mechanism",
      "status": "Implemented",
      "notes": "Using industry-standard security practices"
    }
  ],
  "repo_scan": false
}
```

**Response:**
```json
{
  "success": true,
  "document_id": "doc_123456789",
  "filename": "My_Awesome_Project_PRD.md",
  "markdown_content": "# Product Requirements Document\n\n## Executive Summary\n...",
  "quality_score": {
    "score": 95,
    "words": 2847,
    "completeness": "Excellent"
  },
  "generated_at": "2025-08-20T22:30:00Z"
}
```

### **Upload Repository**
```http
POST /api/upload-repo
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: Repository archive (ZIP/TAR)
- `project_name`: Optional project name

**Response:**
```json
{
  "success": true,
  "findings": [
    {
      "claim": "Testing framework detected",
      "evidence": "pytest configuration found",
      "status": "Verified",
      "notes": "Comprehensive test suite"
    }
  ]
}
```

### **Export Document**
```http
GET /api/export/{document_id}/{format}
```

**Parameters:**
- `document_id`: Document identifier
- `format`: Export format (`md`, `html`, `json`, `txt`)

**Response:**
- File download with appropriate content-type

## 🔍 **Validation Service API**

### **Service Health**
```http
GET /
```

**Response:**
```json
{
  "service": "Project Validation Service",
  "version": "1.0.0",
  "status": "active"
}
```

### **Validate Project Upload**
```http
POST /validate/upload
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: Project archive (ZIP/TAR/TAR.GZ)
- `project_name`: Optional project name

**Response:**
```json
{
  "validation_id": "val_123456789",
  "status": "processing",
  "message": "Analysis started"
}
```

### **Validate Git Repository**
```http
POST /validate/git
Content-Type: application/json
```

**Request Body:**
```json
{
  "git_url": "https://github.com/user/repo.git",
  "branch": "main",
  "project_name": "My Project"
}
```

**Response:**
```json
{
  "validation_id": "val_123456789",
  "status": "processing",
  "message": "Repository cloning started"
}
```

### **Get Validation Status**
```http
GET /validate/{validation_id}/status
```

**Response:**
```json
{
  "validation_id": "val_123456789",
  "status": "processing",
  "progress": 75,
  "message": "Analyzing code quality...",
  "estimated_completion": "2025-08-20T22:35:00Z"
}
```

### **Get Validation Results**
```http
GET /validate/{validation_id}/results
```

**Response:**
```json
{
  "validation_id": "val_123456789",
  "status": "completed",
  "project_name": "My Project",
  "scores": {
    "security": 95,
    "quality": 88,
    "architecture": 92,
    "overall": 92
  },
  "analysis": {
    "security_features": ["authentication", "validation", "encryption"],
    "quality_practices": ["testing", "documentation", "ci_cd"],
    "architecture_patterns": ["Microservices", "Layered"]
  },
  "recommendations": [
    "Add comprehensive API documentation",
    "Implement automated security scanning",
    "Enhance error handling coverage"
  ],
  "detailed_findings": {
    "files_analyzed": 127,
    "lines_of_code": 15420,
    "test_coverage": 85.2,
    "security_issues": 2,
    "code_quality_issues": 5
  },
  "completed_at": "2025-08-20T22:34:15Z"
}
```

### **Download Validation Report**
```http
GET /validate/{validation_id}/report/download
```

**Response:**
- Markdown report file download

## 📊 **Monitoring & Metrics**

### **Detailed Health Check**
```http
GET /api/health/detailed
```

**Response:**
```json
{
  "status": "healthy",
  "system": {
    "status": "healthy",
    "checks": {
      "memory": {
        "status": "healthy",
        "usage_percent": 45.2,
        "available_gb": 6.8
      },
      "cpu": {
        "status": "healthy",
        "usage_percent": 12.5
      },
      "disk": {
        "status": "healthy",
        "usage_percent": 23.1,
        "free_gb": 156.7
      }
    }
  },
  "dependencies": {
    "status": "healthy",
    "checks": {
      "fastapi": {"status": "healthy"},
      "uvicorn": {"status": "healthy"},
      "pydantic": {"status": "healthy"}
    }
  },
  "performance": {
    "uptime_seconds": 86400,
    "requests": {
      "total": 1247,
      "success": 1198,
      "failed": 49,
      "success_rate": 96.07
    },
    "performance": {
      "avg_response_time_ms": 245.6,
      "requests_per_minute": 8.7
    }
  }
}
```

### **Performance Metrics**
```http
GET /api/metrics
```

**Response:**
```json
{
  "uptime_seconds": 86400,
  "uptime_formatted": "1h 0m 0s",
  "requests": {
    "total": 1247,
    "success": 1198,
    "failed": 49,
    "success_rate": 96.07
  },
  "performance": {
    "avg_response_time_ms": 245.6,
    "requests_per_minute": 8.7
  },
  "system": {
    "memory_usage_percent": 45.2,
    "cpu_usage_percent": 12.5,
    "active_users": 23
  }
}
```

## 🔧 **Error Handling**

### **Error Response Format**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid project type specified",
    "details": {
      "field": "project_type",
      "allowed_values": ["web-app", "mobile-app", "api", "desktop", "library"]
    },
    "timestamp": "2025-08-20T22:30:00Z",
    "request_id": "req_123456789"
  }
}
```

### **HTTP Status Codes**
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid API key)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error
- `503` - Service Unavailable

### **Common Error Codes**
- `VALIDATION_ERROR` - Request validation failed
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INVALID_API_KEY` - Authentication failed
- `RESOURCE_NOT_FOUND` - Requested resource doesn't exist
- `PROCESSING_ERROR` - Error during document generation
- `UPLOAD_ERROR` - File upload failed
- `TIMEOUT_ERROR` - Request timed out

## 📚 **SDK Examples**

### **Python SDK**
```python
import requests

class BlueprintGeneratorClient:
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def generate_document(self, project_data):
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=project_data,
            headers=self.headers
        )
        return response.json()
    
    def validate_repository(self, git_url, branch="main"):
        data = {"git_url": git_url, "branch": branch}
        response = requests.post(
            f"{self.base_url}/validate/git",
            json=data,
            headers=self.headers
        )
        return response.json()

# Usage
client = BlueprintGeneratorClient("http://localhost:8001")
result = client.generate_document({
    "project": "My Project",
    "modules": ["claims"],
    "tags": {"doc_type": "readme", "project_type": "web-app"}
})
```

### **JavaScript SDK**
```javascript
class BlueprintGeneratorClient {
    constructor(baseUrl, apiKey = null) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Content-Type': 'application/json'
        };
        if (apiKey) {
            this.headers['Authorization'] = `Bearer ${apiKey}`;
        }
    }
    
    async generateDocument(projectData) {
        const response = await fetch(`${this.baseUrl}/api/generate`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(projectData)
        });
        return await response.json();
    }
    
    async validateRepository(gitUrl, branch = 'main') {
        const response = await fetch(`${this.baseUrl}/validate/git`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ git_url: gitUrl, branch })
        });
        return await response.json();
    }
}

// Usage
const client = new BlueprintGeneratorClient('http://localhost:8001');
const result = await client.generateDocument({
    project: 'My Project',
    modules: ['claims'],
    tags: { doc_type: 'readme', project_type: 'web-app' }
});
```

## 🔗 **Webhooks**

### **Webhook Configuration**
```http
POST /api/webhooks
Content-Type: application/json
```

**Request Body:**
```json
{
  "url": "https://your-app.com/webhook",
  "events": ["document.generated", "validation.completed"],
  "secret": "your-webhook-secret"
}
```

### **Webhook Payload**
```json
{
  "event": "document.generated",
  "data": {
    "document_id": "doc_123456789",
    "project": "My Project",
    "doc_type": "prd",
    "quality_score": 95,
    "generated_at": "2025-08-20T22:30:00Z"
  },
  "timestamp": "2025-08-20T22:30:01Z"
}
```

---

**📞 Need Help?**

- **API Support**: api-support@blueprintgeneratorpro.com
- **Documentation**: https://docs.blueprintgeneratorpro.com
- **Status Page**: https://status.blueprintgeneratorpro.com

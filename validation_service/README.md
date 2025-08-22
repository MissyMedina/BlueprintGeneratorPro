# 🔍 Project Validation Service

A professional, standalone service that validates any codebase using the same powerful analysis engine from the Guidance Blueprint Kit Pro. Turn your project analysis capabilities into a service that others can use!

## 🌟 Features

### 📊 Comprehensive Analysis
- **Security Assessment** - Authentication, encryption, validation, security headers
- **Quality Evaluation** - Testing, documentation, linting, CI/CD, error handling  
- **Architecture Review** - Patterns, structure, scalability indicators
- **Technology Detection** - Automatic identification of frameworks and tools
- **Improvement Recommendations** - Actionable suggestions for enhancement

### 🚀 Multiple Input Methods
- **📁 Local Folder Analysis** - Direct folder scanning with File System Access API
- **📦 Archive Upload** - ZIP/TAR file upload and analysis
- **🔗 Git Repository** - Clone and analyze any public/private Git repo
- **⚡ Async Processing** - Background processing with status polling

### 🛠️ Developer-Friendly
- **REST API** - Clean, documented API endpoints
- **Python SDK** - Easy-to-use client library
- **Docker Ready** - Containerized deployment
- **Swagger Docs** - Interactive API documentation
- **Health Checks** - Built-in monitoring and status endpoints

## 🚀 Quick Start

### Option 1: Direct Python
```bash
# Clone the repository
git clone <your-repo>
cd validation_service

# Install dependencies
pip install -r requirements.txt

# Start the service
python main.py
```

### Option 2: Docker
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run directly
docker build -t validation-service .
docker run -p 8002:8002 validation-service
```

### Option 3: Production with Redis
```bash
# Run with Redis for production
docker-compose --profile production up
```

## 📖 API Usage

### Health Check
```bash
curl http://localhost:8002/
```

### Validate Uploaded Project
```bash
curl -X POST "http://localhost:8002/validate/upload" \
  -F "file=@project.zip" \
  -F "project_name=MyProject"
```

### Validate Git Repository
```bash
curl -X POST "http://localhost:8002/validate/git" \
  -H "Content-Type: application/json" \
  -d '{
    "git_url": "https://github.com/user/repo.git",
    "project_name": "MyRepo",
    "branch": "main"
  }'
```

### Check Validation Status
```bash
curl http://localhost:8002/validate/{validation_id}/status
```

### Get Results
```bash
curl http://localhost:8002/validate/{validation_id}/results
```

## 🐍 Python SDK Usage

### Basic Usage
```python
from client_sdk import ValidationClient, validate_project

# Quick validation
results = validate_project("/path/to/project")
print(f"Security: {results['scores']['security']}/100")
print(f"Quality: {results['scores']['quality']}/100")
print(f"Architecture: {results['scores']['architecture']}/100")
```

### Advanced Usage
```python
client = ValidationClient("http://localhost:8002")

# Validate local folder
results = client.validate_project_folder(
    folder_path="/path/to/project",
    project_name="MyProject",
    validation_profile="comprehensive"
)

# Validate Git repository
results = client.validate_git_repository(
    git_url="https://github.com/user/repo.git",
    branch="main"
)

# Async validation
result = client.validate_project_folder(
    folder_path="/path/to/project",
    wait_for_completion=False
)

# Poll for status
status = client.get_validation_status(result['validation_id'])
while status['status'] == 'processing':
    time.sleep(2)
    status = client.get_validation_status(result['validation_id'])

# Get final results
final_results = client.get_validation_results(result['validation_id'])
```

## 📊 Response Format

### Validation Results
```json
{
  "validation_id": "uuid-here",
  "status": "completed",
  "project_name": "MyProject",
  "scores": {
    "security": 95,
    "quality": 88,
    "architecture": 92
  },
  "analysis": {
    "detected_technologies": {
      "backend": ["python"],
      "frontend": ["html_css"],
      "devops": ["docker"]
    },
    "application_type": {
      "primary_type": "full-stack-web-app",
      "confidence": 0.9
    },
    "security_analysis": {
      "implemented_features": ["authentication", "encryption"],
      "security_score": 95
    }
  },
  "recommendations": [
    "Add comprehensive testing framework",
    "Implement API documentation",
    "Add monitoring and logging"
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔧 Configuration

### Environment Variables
```bash
# Service configuration
PORT=8002
HOST=0.0.0.0

# Redis (optional, for production)
REDIS_URL=redis://localhost:6379

# Git configuration
GIT_TIMEOUT=300
MAX_REPO_SIZE=100MB

# Analysis configuration
MAX_FILE_SIZE=1MB
ANALYSIS_TIMEOUT=300
```

### Validation Profiles
- **comprehensive** - Full analysis (default)
- **security-focused** - Emphasis on security assessment
- **quality-focused** - Emphasis on code quality
- **architecture-focused** - Emphasis on architectural patterns

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client SDK    │    │   REST API      │    │  Analysis Engine│
│                 │───▶│                 │───▶│                 │
│ - Python Client │    │ - FastAPI       │    │ - App Analyzer  │
│ - CLI Tools     │    │ - Async Tasks   │    │ - Score Engine  │
│ - Web Interface │    │ - File Handling │    │ - Report Gen    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Storage       │
                       │                 │
                       │ - In-Memory     │
                       │ - Redis (opt)   │
                       │ - File System   │
                       └─────────────────┘
```

## 🎯 Use Cases

### For Development Teams
```python
# Validate before deployment
results = validate_project("./my-app")
if results['scores']['security'] < 80:
    print("❌ Security score too low for production")
    exit(1)
```

### For Code Review
```python
# Validate pull request
results = validate_git_repo(
    "https://github.com/user/repo.git",
    branch="feature-branch"
)
print(f"Quality improvement: {results['recommendations']}")
```

### For CI/CD Integration
```bash
# In your CI pipeline
python -c "
from client_sdk import validate_project
results = validate_project('.')
exit(0 if all(score >= 80 for score in results['scores'].values()) else 1)
"
```

### For Consulting/Auditing
```python
# Batch validate client projects
projects = ["client1/", "client2/", "client3/"]
for project in projects:
    results = validate_project(project)
    generate_client_report(results)
```

## 📈 Monitoring

### Health Endpoints
- `GET /` - Service info and health
- `GET /health` - Detailed health check
- `GET /metrics` - Prometheus metrics (if enabled)

### Logging
```python
import logging
logging.basicConfig(level=logging.INFO)

# Logs include:
# - Validation requests
# - Processing status
# - Error details
# - Performance metrics
```

## 🔒 Security

### Input Validation
- File size limits
- Archive extraction safety
- Git URL validation
- Content sanitization

### Rate Limiting
```python
# Add rate limiting (example with slowapi)
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/validate/upload")
@limiter.limit("10/minute")
async def validate_upload(...):
    ...
```

## 🚀 Deployment

### Production Checklist
- [ ] Use Redis for result storage
- [ ] Configure rate limiting
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure logging aggregation
- [ ] Set resource limits
- [ ] Enable HTTPS
- [ ] Configure authentication (if needed)

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: validation-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: validation-service
  template:
    metadata:
      labels:
        app: validation-service
    spec:
      containers:
      - name: validation-service
        image: validation-service:latest
        ports:
        - containerPort: 8002
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- 📖 Documentation: `/docs` endpoint when service is running
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions
- 📧 Email: support@yourcompany.com

---

**Transform your code analysis into a service that others can leverage! 🚀**

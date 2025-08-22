#!/usr/bin/env python3
"""
Intelligent Content Generator - Creates contextual, meaningful documentation
Based on user inputs and project details rather than generic templates
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional


class ContentGenerator:
    """Generates contextual documentation content based on user inputs"""

    def __init__(self):
        self.project_types = {
            "web-app": {
                "description": "web application",
                "common_features": [
                    "user authentication",
                    "responsive design",
                    "API integration",
                    "database management",
                ],
                "tech_considerations": [
                    "frontend framework",
                    "backend API",
                    "database choice",
                    "hosting platform",
                ],
                "security_focus": [
                    "XSS protection",
                    "CSRF tokens",
                    "secure authentication",
                    "data validation",
                ],
            },
            "mobile-app": {
                "description": "mobile application",
                "common_features": [
                    "offline functionality",
                    "push notifications",
                    "device integration",
                    "app store deployment",
                ],
                "tech_considerations": [
                    "native vs hybrid",
                    "platform support",
                    "performance optimization",
                    "app store guidelines",
                ],
                "security_focus": [
                    "secure storage",
                    "API security",
                    "biometric authentication",
                    "data encryption",
                ],
            },
            "api": {
                "description": "API/backend service",
                "common_features": [
                    "RESTful endpoints",
                    "authentication",
                    "rate limiting",
                    "documentation",
                ],
                "tech_considerations": [
                    "API design",
                    "database architecture",
                    "scalability",
                    "monitoring",
                ],
                "security_focus": [
                    "API authentication",
                    "input validation",
                    "rate limiting",
                    "secure endpoints",
                ],
            },
            "desktop": {
                "description": "desktop application",
                "common_features": [
                    "native UI",
                    "file system access",
                    "system integration",
                    "offline functionality",
                ],
                "tech_considerations": [
                    "cross-platform support",
                    "installation process",
                    "auto-updates",
                    "system requirements",
                ],
                "security_focus": [
                    "code signing",
                    "secure updates",
                    "local data protection",
                    "privilege management",
                ],
            },
            "library": {
                "description": "library/SDK",
                "common_features": [
                    "clean API",
                    "comprehensive documentation",
                    "examples",
                    "version compatibility",
                ],
                "tech_considerations": [
                    "API design",
                    "backward compatibility",
                    "testing coverage",
                    "distribution",
                ],
                "security_focus": [
                    "secure defaults",
                    "input validation",
                    "dependency management",
                    "vulnerability disclosure",
                ],
            },
        }

    def generate_prd_content(
        self,
        project_name: str,
        project_type: str,
        description: str,
        custom_answers: Dict[str, str],
        focus_area: str,
    ) -> str:
        """Generate a comprehensive PRD with actual project-specific content"""

        project_info = self.project_types.get(project_type, self.project_types["web-app"])

        # Extract key information from custom answers
        target_users = custom_answers.get("target_users", "end users")
        main_problem = custom_answers.get("main_problem", "user needs and business requirements")
        success_metrics = custom_answers.get("success_metrics", "user adoption and satisfaction")

        content = f"""## Product Requirements Document: {project_name}

### Executive Summary

**Project:** {project_name}  
**Type:** {project_info['description'].title()}  
**Purpose:** {description or f"A {project_info['description']} designed to solve {main_problem}"}

**Target Users:** {target_users}

**Core Value Proposition:** {main_problem}

**Success Metrics:** {success_metrics}

### 1. Project Overview

#### 1.1 Problem Statement
{main_problem}

#### 1.2 Solution Approach
{project_name} addresses this challenge by providing a {project_info['description']} that focuses on {focus_area.replace('_', ' ')} while ensuring scalability and user satisfaction.

#### 1.3 Target Audience
- **Primary Users:** {target_users}
- **Secondary Users:** System administrators, support teams
- **Stakeholders:** Product managers, development team, business stakeholders

### 2. Functional Requirements

#### 2.1 Core Features (MUST HAVE)
"""

        # Generate specific features based on project type and user input
        core_features = self._generate_core_features(project_type, custom_answers, focus_area)
        for i, feature in enumerate(core_features, 1):
            content += f"- **F{i:02d}:** {feature}\n"

        content += f"""
#### 2.2 Enhanced Features (SHOULD HAVE)
"""

        enhanced_features = self._generate_enhanced_features(
            project_type, custom_answers, focus_area
        )
        for i, feature in enumerate(enhanced_features, 1):
            content += f"- **E{i:02d}:** {feature}\n"

        content += f"""
#### 2.3 Future Features (MAY HAVE)
"""

        future_features = self._generate_future_features(project_type, custom_answers)
        for i, feature in enumerate(future_features, 1):
            content += f"- **N{i:02d}:** {feature}\n"

        content += f"""

### 3. Technical Requirements

#### 3.1 Performance Requirements
- **Response Time:** < 2 seconds for core operations
- **Throughput:** Support for concurrent users based on {target_users} scale
- **Availability:** 99.9% uptime during business hours
- **Scalability:** Horizontal scaling capability

#### 3.2 Security Requirements
"""

        security_reqs = self._generate_security_requirements(project_type, focus_area)
        for req in security_reqs:
            content += f"- {req}\n"

        content += f"""

#### 3.3 Technology Considerations
"""

        tech_considerations = project_info["tech_considerations"]
        for consideration in tech_considerations:
            content += f"- **{consideration.title()}:** To be determined based on team expertise and project requirements\n"

        content += f"""

### 4. User Experience Requirements

#### 4.1 User Journey
1. **Discovery:** How users find and learn about {project_name}
2. **Onboarding:** Initial setup and first-time user experience
3. **Core Usage:** Primary workflows for {target_users}
4. **Advanced Usage:** Power user features and customization
5. **Support:** Help, documentation, and troubleshooting

#### 4.2 Accessibility Requirements
- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader compatibility
- Mobile-responsive design

### 5. Success Criteria & Metrics

#### 5.1 Key Performance Indicators (KPIs)
- **User Adoption:** {success_metrics}
- **User Satisfaction:** Net Promoter Score (NPS) > 7
- **Performance:** Page load times < 2 seconds
- **Reliability:** < 0.1% error rate

#### 5.2 Acceptance Criteria
- All core features (F01-F{len(core_features):02d}) implemented and tested
- Security requirements validated through penetration testing
- Performance benchmarks met under expected load
- User acceptance testing completed with target users

### 6. Implementation Phases

#### Phase 1: Foundation (Weeks 1-4)
- Core infrastructure setup
- Basic user authentication and authorization
- Essential {project_info['description']} functionality
- Initial security implementation

#### Phase 2: Core Features (Weeks 5-8)
- Implementation of core features F01-F{len(core_features):02d}
- Basic user interface and experience
- Integration testing
- Performance optimization

#### Phase 3: Enhancement (Weeks 9-12)
- Enhanced features E01-E{len(enhanced_features):02d}
- Advanced user interface features
- Comprehensive testing and bug fixes
- Documentation and user guides

#### Phase 4: Launch Preparation (Weeks 13-16)
- Production deployment setup
- Monitoring and alerting implementation
- User training and support materials
- Go-live preparation and rollback plans

### 7. Risks & Mitigation

#### 7.1 Technical Risks
- **Risk:** Performance issues under load
  **Mitigation:** Early performance testing and optimization
- **Risk:** Security vulnerabilities
  **Mitigation:** Regular security audits and penetration testing
- **Risk:** Integration complexity
  **Mitigation:** Proof of concept development and early testing

#### 7.2 Business Risks
- **Risk:** User adoption challenges
  **Mitigation:** User research and iterative design approach
- **Risk:** Scope creep
  **Mitigation:** Clear requirements documentation and change control process

### 8. Dependencies & Assumptions

#### 8.1 Dependencies
- Development team availability and expertise
- Third-party service integrations and APIs
- Infrastructure and hosting platform selection
- Stakeholder approval and feedback cycles

#### 8.2 Assumptions
- Target users have basic technical literacy
- Required infrastructure will be available
- Third-party services will maintain current functionality
- Regulatory requirements will remain stable

---

**Document Version:** 1.0  
**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}  
**Next Review:** {datetime.now().strftime('%Y-%m-%d')} + 2 weeks
"""

        return content

    def _generate_core_features(
        self, project_type: str, custom_answers: Dict[str, str], focus_area: str
    ) -> List[str]:
        """Generate project-specific core features"""
        project_info = self.project_types.get(project_type, self.project_types["web-app"])
        base_features = project_info["common_features"]

        features = []

        # Add base features with context
        for feature in base_features[:3]:  # Take first 3 as core
            features.append(f"{feature.title()} tailored for the target user needs")

        # Add focus-specific features
        if focus_area == "security":
            features.extend(
                [
                    "Multi-factor authentication system",
                    "Data encryption at rest and in transit",
                    "Audit logging and compliance reporting",
                ]
            )
        elif focus_area == "performance":
            features.extend(
                [
                    "Optimized data loading and caching",
                    "Real-time performance monitoring",
                    "Scalable architecture design",
                ]
            )
        elif focus_area == "ux":
            features.extend(
                [
                    "Intuitive user interface design",
                    "Accessibility compliance (WCAG 2.1)",
                    "Mobile-responsive experience",
                ]
            )
        else:  # app (complete)
            features.extend(
                [
                    "Comprehensive user management",
                    "Robust error handling and recovery",
                    "Extensible plugin architecture",
                ]
            )

        return features[:6]  # Limit to 6 core features

    def _generate_enhanced_features(
        self, project_type: str, custom_answers: Dict[str, str], focus_area: str
    ) -> List[str]:
        """Generate enhanced features based on project context"""
        features = [
            "Advanced analytics and reporting dashboard",
            "Integration with popular third-party services",
            "Customizable user preferences and settings",
            "Automated backup and recovery system",
            "Advanced search and filtering capabilities",
        ]

        # Add project-type specific enhancements
        if project_type == "web-app":
            features.append("Progressive Web App (PWA) capabilities")
        elif project_type == "mobile-app":
            features.append("Offline synchronization and conflict resolution")
        elif project_type == "api":
            features.append("GraphQL endpoint with flexible querying")

        return features[:5]  # Limit to 5 enhanced features

    def _generate_future_features(
        self, project_type: str, custom_answers: Dict[str, str]
    ) -> List[str]:
        """Generate future/nice-to-have features"""
        return [
            "AI-powered recommendations and insights",
            "Advanced workflow automation",
            "Multi-language and internationalization support",
            "Advanced collaboration features",
            "Machine learning-based optimization",
        ]

    def _generate_security_requirements(self, project_type: str, focus_area: str) -> List[str]:
        """Generate security requirements based on project type and focus"""
        project_info = self.project_types.get(project_type, self.project_types["web-app"])
        base_security = project_info["security_focus"]

        requirements = []
        for req in base_security:
            requirements.append(
                f"**{req.title()}:** Implementation required with industry best practices"
            )

        # Add focus-specific security requirements
        if focus_area == "security":
            requirements.extend(
                [
                    "**Penetration Testing:** Regular third-party security assessments",
                    "**Compliance:** GDPR, SOC2, and relevant industry standards",
                    "**Incident Response:** Documented security incident response plan",
                ]
            )

        return requirements

    def generate_readme_content(
        self,
        project_name: str,
        project_type: str,
        description: str,
        custom_answers: Dict[str, str],
    ) -> str:
        """Generate a comprehensive README with actual project details"""

        project_info = self.project_types.get(project_type, self.project_types["web-app"])

        installation_method = custom_answers.get("installation_method", "git clone")
        main_features = custom_answers.get("main_features", "Core functionality for user needs")
        tech_stack = custom_answers.get("tech_stack", "Modern web technologies")

        content = f"""# {project_name}

{description or f"A powerful {project_info['description']} designed to solve real-world problems."}

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/user/repo)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/user/repo/releases)

## 🚀 Features

{main_features}

### Key Capabilities
"""

        # Generate specific features based on project type
        features = self._generate_readme_features(project_type, custom_answers)
        for feature in features:
            content += f"- ✅ **{feature}**\n"

        content += f"""

## 🛠️ Technology Stack

**Core Technologies:** {tech_stack}

### Architecture Overview
- **Frontend:** Modern, responsive user interface
- **Backend:** Scalable server architecture
- **Database:** Optimized data storage and retrieval
- **Security:** Industry-standard security practices

## 📦 Installation

### Prerequisites
- Node.js 16+ (for web applications)
- Python 3.8+ (for backend services)
- Git for version control

### Quick Start

```bash
# Clone the repository
git clone https://github.com/user/{project_name.lower().replace(' ', '-')}.git
cd {project_name.lower().replace(' ', '-')}

# Install dependencies
{self._get_install_command(installation_method)}

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Start the application
{self._get_start_command(project_type)}
```

## 🎯 Usage

### Basic Usage

```bash
# Example usage for {project_name}
{self._generate_usage_example(project_type, project_name)}
```

### Advanced Configuration

```yaml
# config.yml example
app:
  name: "{project_name}"
  environment: "development"
  features:
    - authentication
    - analytics
    - notifications
```

## 📚 API Documentation

### Core Endpoints

```http
GET /api/v1/status
POST /api/v1/auth/login
GET /api/v1/data
PUT /api/v1/data/:id
DELETE /api/v1/data/:id
```

### Authentication

```bash
# Get access token
curl -X POST https://api.example.com/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{{"username": "user", "password": "pass"}}'
```

## 🧪 Testing

```bash
# Run unit tests
npm test

# Run integration tests
npm run test:integration

# Run end-to-end tests
npm run test:e2e

# Generate coverage report
npm run test:coverage
```

## 🚀 Deployment

### Production Deployment

```bash
# Build for production
npm run build

# Deploy to production
npm run deploy

# Monitor deployment
npm run monitor
```

### Docker Deployment

```dockerfile
# Dockerfile example
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Code Style

- Follow ESLint configuration
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all contributors who have helped shape {project_name}
- Inspired by best practices in {project_info['description']} development
- Built with modern tools and frameworks

## 📞 Support

- **Documentation:** [docs.example.com]
- **Issues:** [GitHub Issues](https://github.com/user/repo/issues)
- **Discussions:** [GitHub Discussions](https://github.com/user/repo/discussions)
- **Email:** support@example.com

---

**Made with ❤️ by the {project_name} team**
"""

        return content

    def _generate_readme_features(
        self, project_type: str, custom_answers: Dict[str, str]
    ) -> List[str]:
        """Generate README-specific features"""
        project_info = self.project_types.get(project_type, self.project_types["web-app"])

        features = []
        for feature in project_info["common_features"]:
            features.append(feature.title())

        # Add some generic but useful features
        features.extend(
            [
                "Comprehensive documentation",
                "Easy installation and setup",
                "Active community support",
                "Regular updates and maintenance",
            ]
        )

        return features[:6]

    def _get_install_command(self, method: str) -> str:
        """Get appropriate install command"""
        commands = {
            "npm install": "npm install",
            "pip install": "pip install -r requirements.txt",
            "git clone": "git clone [repository-url]",
            "download binary": "# Download from releases page",
            "docker": "docker pull [image-name]",
            "other": "# Follow installation guide",
        }
        return commands.get(method, "npm install")

    def _get_start_command(self, project_type: str) -> str:
        """Get appropriate start command"""
        commands = {
            "web-app": "npm start",
            "mobile-app": "npm run ios # or npm run android",
            "api": "python app.py",
            "desktop": "./app",
            "library": "# Import in your project",
        }
        return commands.get(project_type, "npm start")

    def _generate_usage_example(self, project_type: str, project_name: str) -> str:
        """Generate usage example"""
        examples = {
            "web-app": f"# Open browser to http://localhost:3000\n# Login and explore {project_name} features",
            "mobile-app": f"# Install on device and launch\n# Complete onboarding flow",
            "api": f"curl -X GET http://localhost:8000/api/v1/status",
            "desktop": f"./{project_name.lower()} --help",
            "library": f'import {project_name.lower().replace(" ", "_")}\n{project_name.lower().replace(" ", "_")}.initialize()',
        }
        return examples.get(project_type, f"# Start using {project_name}")


# Global instance
content_generator = ContentGenerator()

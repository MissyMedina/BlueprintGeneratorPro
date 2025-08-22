# 🚀 Guidance Blueprint Kit Pro

**The Ultimate Multi-Purpose Documentation Generator**

Generate professional PRDs, READMEs, MVPs, Application Validators, and Enhancement Plans with intelligent automation and latest standards compliance.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Quality](https://img.shields.io/badge/code%20quality-A+-green.svg)](./docscore.py)

## ✨ Features

- **🎯 Multi-Purpose Generation**: PRDs, READMEs, MVPs, Validators, Enhancement Plans
- **🔍 Intelligent Repository Scanning**: Auto-extracts evidence from your codebase
- **📊 Standards Compliance**: Built-in security, performance, and compliance checks
- **🎨 Modular Design**: Pick only what you need for each document
- **📈 Quality Scoring**: Automated document quality assessment
- **🔧 IDE Integration**: VSCode snippets and Cursor rules included
- **📋 Profile System**: Predefined templates for common use cases

## 🚀 Quick Start

### Basic Usage
```bash
# Generate a full application evaluation
python3 blueprint_pro.py --project "MyApp" --modules claims,prd,operator --claims_scope app

# Security-focused audit
python3 blueprint_pro.py --project "MyApp" --profile sec-audit

# Auto-scan repository for evidence
python3 blueprint_pro.py --project "MyApp" --repo /path/to/repo --modules claims --claims_scope security
```

### Advanced Usage
```bash
# Custom tags and evidence seeding
python3 blueprint_pro.py --project "MyApp" \
  --modules claims,prd,appendices \
  --evidence_csv evidence_seed.csv \
  --tag sprint=34 --tag owner=missy \
  --out docs/MyApp-evaluation.md

# Skip certain auto-scan categories
python3 blueprint_pro.py --project "MyApp" \
  --repo /path/to/repo \
  --skip_categories security,tests \
  --max_findings 25
```

## 📋 Available Modules

| Module | Purpose | Use Cases |
|--------|---------|-----------|
| `claims` | Reality Check (claims vs. reality) | Validation, Audits, Compliance |
| `prd` | Product Requirements Document | Feature Planning, Enhancement |
| `operator` | AI/IDE Collaboration Guide | Development Workflow |
| `identity` | Style & Tone Guidelines | Brand Consistency |
| `appendices` | Evidence, Risks, Glossary | Documentation, Reference |

## 🎯 Claims Scope Options

| Scope | Focus Area | Best For |
|-------|------------|----------|
| `app` | Complete application | Full evaluations, MVPs |
| `security` | Security & compliance | Audits, penetration testing prep |
| `data` | Data handling & privacy | GDPR compliance, data architecture |
| `performance` | Speed & scalability | Performance optimization |
| `reliability` | Uptime & resilience | SRE, operations readiness |
| `privacy` | Privacy compliance | GDPR, CCPA, privacy audits |
| `compliance` | Regulatory compliance | SOC2, HIPAA, industry standards |
| `ux` | User experience | UX reviews, accessibility |

## 🔧 Built-in Profiles

```bash
# Full evaluation (claims + PRD + operator + appendices)
--profile full-eval

# Security audit (claims + appendices, security scope)
--profile sec-audit

# Operations readiness (claims + operator + appendices, reliability scope)
--profile ops-readiness

# UX review (claims + PRD + appendices, UX scope)
--profile ux-review
```

## 🔍 Intelligent Repository Scanning

The Pro version automatically scans your repository for:

- **🔐 Security**: OpenAPI security schemes, secrets detection, dependency pinning
- **📦 Dependencies**: Version pinning, vulnerability scanning setup
- **🐳 Docker**: Base image pinning, security best practices
- **🔄 CI/CD**: Security scanning tools integration
- **🧪 Testing**: Coverage configuration, acceptance tests

## 📊 Quality Scoring

Evaluate your documentation quality:

```bash
python3 docscore.py your-document.md
```

Scoring factors:
- Section coverage and completeness
- Claims table richness with evidence
- Requirements density (MUST/SHOULD/MAY)
- Acceptance tests presence
- Checklist availability
- Overall content depth

## 🛠️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd GuidanceBlueprintKit-Pro
   ```

2. **No dependencies required** - Pure Python 3.7+

3. **Optional: Install VSCode snippets**
   ```bash
   cp -r vscode/snippets ~/.vscode/snippets/
   ```

## 📁 Project Structure

```
GuidanceBlueprintKit-Pro/
├── blueprint_pro.py      # Main generator script
├── docscore.py          # Quality scoring tool
├── profiles.json        # Predefined profiles
├── evidence_seed.csv    # Sample evidence data
├── Makefile            # Build automation
├── cursor-rules.md     # IDE collaboration rules
└── vscode/             # IDE integration
    └── snippets/       # Code snippets
```

## 🎨 Use Cases

### 📝 PRD Generation
Perfect for product managers and developers creating comprehensive product requirements documents with built-in quality checks.

### 📖 README Creation
Generate professional README files with proper structure, badges, and documentation standards.

### 🚀 MVP Planning
Create minimal viable product plans with clear acceptance criteria and phased development approach.

### ✅ Application Validation
Audit existing applications against security, performance, and compliance standards.

### 🔧 Enhancement Planning
Identify improvement opportunities and create actionable enhancement roadmaps.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

Built with ❤️ for developers who value quality documentation and systematic approaches to software development.

---

**Ready to transform your documentation workflow?** Start with a simple command and watch your project documentation come to life!

#!/usr/bin/env python3
"""
Guidance Blueprint Kit — PRO (profiles + evidence seeding)

New:
  --profile <name>     : load default modules/claims_scope from profiles.json
  --evidence_csv <fp>  : prefill Claims table rows from a CSV with columns:
                         claim,evidence,status,notes
  --tag <key=value>    : add custom front-matter tags (repeatable)

Examples:
  python blueprint_pro.py --project "HypeHub" --profile sec-audit --evidence_csv evidence_seed.csv
  python blueprint_pro.py --project "BlockSense" --modules claims,operator --claims_scope reliability --tag sprint=34 --tag owner=missy
"""

import argparse, os, sys, json, datetime, csv, re

TODAY = datetime.date.today().isoformat()

def load_profiles():
    here = os.path.dirname(os.path.abspath(__file__))
    pf = os.path.join(here, "profiles.json")
    if os.path.exists(pf):
        with open(pf, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def parse_tags(tag_list):
    tags = {}
    for t in tag_list or []:
        if "=" in t:
            k,v = t.split("=",1)
            tags[k.strip()] = v.strip()
    return tags

HEADER = """---
generated: {today}
project: {project}
modules: {modules}
claims_scope: {claims_scope}
{extra_tags}
---

"""

SCOPE = """## 0) Scope & Context

- **Project:** {project}
- **Date:** {today}
- **Audience & Goals:** [who needs this and why]
- **Environment/Stack:** [OS, runtimes, frameworks, data sources]
- **Constraints/Assumptions:** [deadlines, budgets, SLAs, compliance]
- **Assets:** [repos, docs, dashboards, tickets]

"""

def claims_table(scope, rows):
    header = f"""## 1) Reality Check — Claims vs. Reality ({scope})

**Instructions:** List concrete claims/promises in scope = **{scope}**. Attach evidence and mark status.

| Claim (in-scope) | Evidence (file/line, output, URL) | Status (✅/⚠️/❌) | Notes |
|---|---|---|---|
"""
    if not rows:
        return header + "|  |  |  |  |\n\n" + ARCH_SNAPSHOT
    body = "".join([f"| {r.get('claim','')} | {r.get('evidence','')} | {r.get('status','')} | {r.get('notes','')} |\n" for r in rows])
    return header + body + "\n" + ARCH_SNAPSHOT

ARCH_SNAPSHOT = """### Architecture & Readiness Snapshot
- **Design & Boundaries:** [loose or tight coupling, clear seams?]
- **Dependencies:** [pinned versions, SBOM, unnecessary libs]
- **Validation & Error Handling:** [input checks, retries, dead letters]
- **Observability:** [logs, metrics, tracing, dashboards]
- **Security:** [authN/Z model, secrets mgmt, threat model, least privilege]
- **Compliance/Privacy:** [PII handling, DSRs, retention]
- **Performance/Resilience:** [load profile, latency, circuit breakers]
- **Production Readiness:** [can we ship safely now?]

"""

PRD = """## 2) Upgrade PRD — From "works" to "wow"

### 2.1 Top Opportunities (Summary)
| Opportunity | Category | Why It Matters | Impact | Proposed Fix |
|---|---|---|---|---|
|  |  |  |  |  |

### 2.2 Feature Spec (repeat per item)
**Feature:** [name]  
**Motivation:** [user value + evaluator flag]  
**Requirements (MUST/SHOULD/MAY):**
- MUST: […]
- SHOULD: […]
- MAY: […]
**API/UX Notes:** […]
**Dependencies & Risks:** […]
**Acceptance Tests:** [… (what proof shows this is done?)]

### 2.3 Non-Feature Enhancements
- **Testing:** [critical path coverage, fuzzing]
- **CI/CD:** [triggers, quality gates, protected branches]
- **Monitoring:** [SLOs/alerts, dashboards]
- **Security hardening:** [SAST/DAST, SBOM, threat model updates]
- **Cost/Performance:** [benchmarks, budgets]

### 2.4 Phasing & Timeline
- **Phase 1 (Foundation):** […]
- **Phase 2 (User value):** […]
- **Phase 3 (AI assist):** […]
- **Phase 4 (Perf/Cost):** […]
"""

OPERATOR = """## 3) Operator Guide — How to Work With the IDE/AI

**Context to provide on every request (copy/paste scaffold):**
```
Context:
- OS: [..]; Repo: [..]; File(s): [..:Lxx-Lyy]
- Error/output: [...]
Task:
Constraints:
Expected outcome:
Verification steps/tests:
```

**Edit Discipline:**
- Read surrounding 50+ lines and map imports before edits.
- Group related edits; show minimal diffs; never "..." skip code in critical paths.
- Stop after 3 failed loops and ask for a different approach.

**Search & Verify Loop:**
1) Semantic search → 2) grep/symbol search → 3) read → 4) edit → 5) run tests → 6) review diffs/logs → 7) rollback if needed.

**Terminal Hygiene:**
- `cd` explicitly; print long outputs with pagination.
- Red flags: deletes, chmod 777, plaintext secrets.

**Quality Gates:**
- Lint & unit tests must pass before merge.
- Require at least one acceptance proof per PRD item.
"""

IDENTITY = """## 4) (Optional) Identity & Style Capsule

- **Voice/Tone:** encouraging, witty, plain-English first.
- **Explaining style:** step-down complexity, analogies, "teach then do".
- **Engagement:** brief humor, concrete examples, verify understanding.
- **Adaptation rules:** vary directness for incident vs. ideation.
- **Never say:** [list], **Signature moves:** [list].
"""

APPENDICES = """## 5) Appendices

### Evidence Index
- [links/files/lines, tickets, dashboards]

### Risk Register
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
|  |  |  |  |

### Glossary
- [term]: [definition]

### Quick Checklists
- **Reality Check (15 min):** collect claims → find proof → mark gaps → top 3 risks.
- **PRD Cut (60 min):** convert gaps to MUST/SHOULD/MAY → acceptance tests → phases.
- **Operator Refresh:** add request scaffolds → enforce loop → quality gates.
"""

def assemble(project, modules, claims_scope, evidence_rows, tags):
    extra_tags = ""
    for k,v in (tags or {}).items():
        extra_tags += f"{k}: {v}\n"
    md = HEADER.format(today=TODAY, project=project, modules=",".join(modules), claims_scope=claims_scope, extra_tags=extra_tags)
    md += SCOPE.format(project=project, today=TODAY)
    if "claims" in modules:
        md += claims_table(claims_scope, evidence_rows)
    if "prd" in modules:
        md += PRD
    if "operator" in modules:
        md += OPERATOR
    if "identity" in modules:
        md += IDENTITY
    if "appendices" in modules:
        md += APPENDICES
    return md

def read_evidence_csv(fp):
    rows = []
    if not fp: return rows
    with open(fp, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "claim": r.get("claim","").strip(),
                "evidence": r.get("evidence","").strip(),
                "status": r.get("status","").strip(),
                "notes": r.get("notes","").strip()
            })
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", help="Path to repo to auto-extract evidence (optional, non-fatal)")
    ap.add_argument("--max_findings", type=int, default=50, help="Limit auto findings")
    ap.add_argument("--skip_categories", help="Comma list: security,tests")
    ap.add_argument("--project", required=True)
    ap.add_argument("--modules", help="Comma list: claims,prd,operator,identity,appendices")
    ap.add_argument("--claims_scope", choices=["app","security","data","performance","reliability","privacy","compliance","ux"])
    ap.add_argument("--profile", help="Profile name from profiles.json")
    ap.add_argument("--evidence_csv", help="CSV path with columns claim,evidence,status,notes")
    ap.add_argument("--tag", action="append", help="Add front-matter tag key=value (repeatable)")
    ap.add_argument("--out", help="Output path (.md)")
    args = ap.parse_args()

    profs = load_profiles()
    modules = None
    scope = None

    if args.profile:
        p = profs.get(args.profile)
        if not p:
            print(f"Unknown profile: {args.profile}. Known: {', '.join(profs.keys())}", file=sys.stderr); sys.exit(2)
        modules = p["modules"]
        scope = p["claims_scope"]

    if args.modules:
        modules = [m.strip().lower() for m in args.modules.split(",") if m.strip()]
    if not modules:
        print("No modules selected. Use --profile or --modules.", file=sys.stderr); sys.exit(2)

    if args.claims_scope:
        scope = args.claims_scope
    if not scope:
        scope = "app"

    auto_rows = collect_repo_findings(args.repo, args.skip_categories, args.max_findings) if args.repo else []
    csv_rows = read_evidence_csv(args.evidence_csv)
    evidence_rows = _merge_evidence(auto_rows, csv_rows)
    tags = parse_tags(args.tag)

    md = assemble(args.project, modules, scope, evidence_rows, tags)

    if args.out:
        out_path = args.out
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    else:
        safe_proj = "".join(ch for ch in args.project if ch.isalnum() or ch in ("-","_")).strip() or "Project"
        stamp = TODAY
        mslug = "-".join(modules)
        out_path = f"{stamp}-{safe_proj}-{mslug}.md"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"Wrote {out_path}")



# ---------------- Repo Evidence Extractor (safe & optional) ----------------

SAFE_MAX_BYTES = 1_000_000  # per file soft limit

def _safe_read(fp):
    try:
        if os.path.getsize(fp) > SAFE_MAX_BYTES:
            return ""
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""

def _glob(root, patterns):
    matches = []
    for dirpath, _, files in os.walk(root):
        for name in files:
            for pat in patterns:
                if re.fullmatch(pat.replace(".", r"\.").replace("*", r".*"), name):
                    matches.append(os.path.join(dirpath, name))
                    break
    return matches

def _scan_openapi(root):
    findings = []
    for fp in _glob(root, ["openapi.yaml", "openapi.yml", "swagger.json"]):
        txt = _safe_read(fp)
        if not txt: 
            continue
        # auth presence
        if re.search(r"securitySchemes", txt, re.I):
            findings.append({
                "claim": "OpenAPI defines security schemes",
                "evidence": f"{fp}: securitySchemes present",
                "status": "✅",
                "notes": "Auth defined at spec level"
            })
        # unsecured endpoints (very heuristic)
        if re.search(r"paths:|\"paths\"", txt):
            if re.search(r"security:\s*\[\s*\]\s*", txt) or re.search(r"\"security\"\s*:\s*\[\s*\]", txt):
                findings.append({
                    "claim": "Some endpoints allow anonymous access",
                    "evidence": f"{fp}: empty security arrays detected",
                    "status": "⚠️",
                    "notes": "Verify health probes/webhooks"
                })
    return findings

def _scan_dependencies(root):
    findings = []
    # Python
    for fp in _glob(root, ["requirements.txt", "Pipfile", "Pipfile.lock"]):
        txt = _safe_read(fp)
        if not txt: 
            continue
        if "==" not in txt:
            findings.append({
                "claim": "Dependencies are pinned",
                "evidence": f"{fp}: missing exact pins for some packages",
                "status": "⚠️",
                "notes": "Prefer exact versions for reproducibility"
            })
        else:
            findings.append({
                "claim": "Dependencies use exact version pins",
                "evidence": f"{fp} contains '=='",
                "status": "✅",
                "notes": "Good for reproducible builds"
            })
    # Node
    for fp in _glob(root, ["package.json"]):
        txt = _safe_read(fp)
        if not txt: 
            continue
        if re.search(r'\"\^|\"~', txt):
            findings.append({
                "claim": "Node dependencies are pinned",
                "evidence": f"{fp}: found ^ or ~ version ranges",
                "status": "⚠️",
                "notes": "Replace ranges with exact versions for determinism"
            })
        else:
            findings.append({
                "claim": "Node dependencies use exact versions",
                "evidence": f"{fp}: no ^ or ~ detected",
                "status": "✅",
                "notes": "Deterministic installs"
            })
    return findings

def _scan_env_and_secrets(root):
    findings = []
    for fp in _glob(root, [".env", ".env.example", "config.yml", "config.yaml"]):
        txt = _safe_read(fp)
        if not txt: 
            continue
        if re.search(r"(?i)(secret|api[_-]?key|token)\s*[:=]\s*[^\s]+", txt):
            findings.append({
                "claim": "Secrets are stored securely",
                "evidence": f"{fp}: inline secrets detected",
                "status": "❌",
                "notes": "Move to a secrets manager; never store plaintext secrets"
            })
        else:
            findings.append({
                "claim": "No plaintext secrets committed",
                "evidence": f"{fp}: no inline secrets found",
                "status": "✅",
                "notes": "Still verify via repo history"
            })
    return findings

def _scan_docker(root):
    findings = []
    for fp in _glob(root, ["Dockerfile", "Dockerfile.*"]):
        txt = _safe_read(fp)
        if not txt: 
            continue
        if re.search(r"FROM\s+.+:latest", txt, re.I):
            findings.append({
                "claim": "Base image uses immutable (pinned) tag",
                "evidence": f"{fp}: uses ':latest'",
                "status": "⚠️",
                "notes": "Pin to a digest or fixed version tag"
            })
        else:
            findings.append({
                "claim": "Base image is pinned",
                "evidence": f"{fp}: no ':latest' detected",
                "status": "✅",
                "notes": "Good for reproducible builds"
            })
    return findings

def _scan_ci(root):
    findings = []
    for fp in _glob(root, [".github/workflows/.*\.yml", ".github/workflows/.*\.yaml"]):
        txt = _safe_read(fp)
        if not txt: 
            continue
        if re.search(r"trivy|snyk|bandit|semgrep|codeql", txt, re.I):
            findings.append({
                "claim": "CI includes security scans",
                "evidence": f"{fp}: scan tool referenced",
                "status": "✅",
                "notes": "Security scanning configured"
            })
        else:
            findings.append({
                "claim": "CI includes security scans",
                "evidence": f"{fp}: no common scanners found",
                "status": "⚠️",
                "notes": "Add SAST/DAST or dependency scans"
            })
    return findings

def _scan_tests(root):
    findings = []
    for fp in _glob(root, ["pytest.ini", "pyproject.toml", "package.json", "jest.config.js", "jest.config.cjs"]):
        txt = _safe_read(fp)
        if not txt: 
            continue
        if re.search(r"cov|coverage|nyc", txt, re.I):
            findings.append({
                "claim": "Coverage tooling is configured",
                "evidence": f"{fp}: coverage/nyc keywords present",
                "status": "✅",
                "notes": "Collect reports and set thresholds"
            })
    # presence of acceptance or e2e tests
    for dirpath, _, files in os.walk(root):
        for name in files:
            if re.search(r"(acceptance|e2e).*\.(py|js|ts|sh)$", name, re.I):
                findings.append({
                    "claim": "Acceptance/E2E tests exist",
                    "evidence": os.path.join(dirpath, name),
                    "status": "✅",
                    "notes": "Hook to Acceptance Harness"
                })
                break
    return findings

def collect_repo_findings(root, skip_categories=None, max_findings=50):
    try:
        if not root or not os.path.isdir(root):
            return []
    except Exception:
        return []
    skip = set((skip_categories or "").split(",")) if skip_categories else set()
    allf = []
    if "security" not in skip:
        allf += _scan_openapi(root)
        allf += _scan_env_and_secrets(root)
        allf += _scan_dependencies(root)
        allf += _scan_docker(root)
        allf += _scan_ci(root)
    if "tests" not in skip:
        allf += _scan_tests(root)
    # fold to max
    return allf[:max_findings]

def _merge_evidence(auto_rows, csv_rows):
    return (auto_rows or []) + (csv_rows or [])

if __name__ == "__main__":
    main()

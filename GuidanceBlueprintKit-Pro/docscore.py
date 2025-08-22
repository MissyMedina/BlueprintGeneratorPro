#!/usr/bin/env python3
"""
Guidance Doc Scorer — computes a heuristic quality score (0-100)
Signals:
- Section coverage (Scope, Claims, PRD, Operator, Identity, Appendices)
- Claims table rows count (>2 better), presence of statuses, evidence links
- MUST/SHOULD/MAY density
- "Acceptance Tests" presence
- Checklist presence
- Word count per included section
"""
import json
import math
import re
import sys


def read(fp):
    with open(fp, "r", encoding="utf-8") as f:
        return f.read()


def count(pattern, s, flags=re.I):
    return len(re.findall(pattern, s, flags))


def has(pattern, s, flags=re.I):
    return re.search(pattern, s, flags) is not None


def score(md):
    total = 0
    parts = {}

    # sections
    sec_points = 0
    for sec in [
        r"## 0\) Scope & Context",
        r"## 1\) Reality Check",
        r"## 2\) Upgrade PRD",
        r"## 3\) Operator Guide",
        r"## 4\) \(Optional\) Identity",
        r"## 5\) Appendices",
    ]:
        if has(sec, md):
            sec_points += 5
    total += sec_points
    parts["sections"] = sec_points

    # claims table richness
    table_rows = count(r"\n\| .* \| .* \| .* \| .* \|\n", md)
    statuses = count(r"✅|⚠️|❌", md)
    evid_links = count(r"http[s]?://|\.py:|\.md:|L\d+|§|\.\w{2,3}", md)
    claim_points = min(
        25, table_rows * 3 + min(10, statuses) + min(10, evid_links // 3)
    )
    total += claim_points
    parts["claims"] = claim_points

    # MUST/SHOULD/MAY density + acceptance tests
    rqm = count(r"\bMUST\b", md) + count(r"\bSHOULD\b", md) + count(r"\bMAY\b", md)
    acc = count(r"Acceptance Tests", md)
    rqm_points = min(20, rqm) + min(5, acc * 2)
    total += rqm_points
    parts["requirements"] = rqm_points

    # checklists
    check_points = 0
    if has(r"Quick Checklists", md):
        check_points += 5
    total += check_points
    parts["checklists"] = check_points

    # word count factor
    words = len(md.split())
    wc_points = min(15, max(0, (words - 300) // 200))
    total += wc_points
    parts["length"] = wc_points

    return {"score": min(100, total), "breakdown": parts, "words": words}


if __name__ == "__main__":
    fp = sys.argv[1]
    res = score(read(fp))
    print(json.dumps(res, indent=2))

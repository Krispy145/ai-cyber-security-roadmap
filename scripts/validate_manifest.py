#!/usr/bin/env python3
import json, sys, datetime
from pathlib import Path

MANIFEST_PATH = Path("manifest.json")
ALLOWED_REPO_STATUS = {"active","planned","scaffolded","stub","done"}
ALLOWED_MS_STATUS   = {"todo","in_progress","done","planned"}

def parse_date_any(s: str):
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(s, fmt)
        except Exception:
            pass
    return None

def url_like(s: str) -> bool:
    return isinstance(s, str) and s.startswith(("http://","https://"))

def main():
    errors, warnings = [], []

    if not MANIFEST_PATH.exists():
        print("ERROR: manifest.json not found.")
        sys.exit(2)

    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: manifest.json invalid JSON: {e}")
        sys.exit(2)

    # updated
    upd = manifest.get("updated")
    if not upd or not parse_date_any(str(upd)):
        errors.append("`updated` missing or invalid date format.")

    # progress
    prog = manifest.get("progress", {})
    for k in ("learning","projects","backend","flutter","react","react_native","certifications"):
        v = prog.get(k)
        if not isinstance(v, int) or not (0 <= v <= 100):
            errors.append(f"`progress.{k}` must be 0–100 int (got {v}).")

    # focus
    sp = manifest.get("focus", {}).get("security_prep_start")
    if sp and not parse_date_any(str(sp)):
        errors.append("`focus.security_prep_start` invalid date format.")

    # repositories
    repos = manifest.get("repositories", [])
    if not isinstance(repos, list) or not repos:
        errors.append("`repositories` must be a non-empty list.")
        repos = []

    seen_repo_names = set()
    for i, r in enumerate(repos, 1):
        name, url, desc = r.get("name"), r.get("url"), r.get("description")
        status, topics, target = (r.get("status") or "").lower(), r.get("topics", []), r.get("target")

        if not name:
            errors.append(f"repositories[{i}].name required.")
        elif name in seen_repo_names:
            errors.append(f"Duplicate repository name '{name}'.")
        seen_repo_names.add(name)

        if not url_like(url):
            errors.append(f"repositories[{i}] {name}: invalid url.")
        if not desc:
            errors.append(f"repositories[{i}] {name}: description required.")
        if "short_description" not in r:
            warnings.append(f"repositories[{i}] {name}: missing short_description (recommended).")

        if status and status not in ALLOWED_REPO_STATUS:
            errors.append(f"repositories[{i}] {name}: invalid status '{status}'.")

        if target not in (None, "") and parse_date_any(str(target)) is None:
            errors.append(f"repositories[{i}] {name}: invalid target date format.")

        if topics is not None:
            if not isinstance(topics, list) or any(not isinstance(t, str) for t in topics):
                errors.append(f"repositories[{i}] {name}: topics must be string list.")
            elif len(topics) > 8:
                warnings.append(f"repositories[{i}] {name}: more than 8 topics (will truncate).")
            for t in topics:
                if len(t) > 30:
                    warnings.append(f"repositories[{i}] {name}: topic '{t}' >30 chars.")

    # milestones
    milestones = manifest.get("milestones", [])
    if not isinstance(milestones, list):
        errors.append("`milestones` must be a list.")
        milestones = []

    seen_ids, seen_pairs = set(), set()
    for j, m in enumerate(milestones, 1):
        mid, title = m.get("id"), m.get("title")
        status = (m.get("status") or "").lower()
        due, date, repo = m.get("due"), m.get("date"), m.get("repo")

        if not mid:
            errors.append(f"milestones[{j}]: missing id.")
        elif mid in seen_ids:
            errors.append(f"Duplicate milestone id '{mid}'.")
        seen_ids.add(mid)

        if not title:
            errors.append(f"milestones[{j}] {mid}: title required.")

        if status not in ALLOWED_MS_STATUS:
            errors.append(f"milestones[{j}] {mid}: invalid status '{status}'.")

        if not (due or date):
            errors.append(f"milestones[{j}] {mid}: must have due or date.")
        for lbl, val in (("due", due), ("date", date)):
            if val and parse_date_any(str(val)) is None:
                errors.append(f"milestones[{j}] {mid}: {lbl} invalid date format.")

        # repo must reference valid repository name if not null
        if repo and repo not in seen_repo_names:
            errors.append(f"milestones[{j}] {mid}: repo '{repo}' not in repositories[].name.")

        # duplicate title+due detection within same repository
        pair = (repo or "", title.strip().lower() if title else "", due or date or "")
        if pair in seen_pairs:
            errors.append(f"Duplicate milestone with same title+date in repo '{repo}': '{title}' {due or date}.")
        seen_pairs.add(pair)

    # next_milestone consistency
    nm = manifest.get("next_milestone")
    if nm:
        nm_id = nm.get("id")
        if not nm_id or nm_id not in seen_ids:
            errors.append("`next_milestone.id` not found among milestones[].id.")
        if nm.get("due") and parse_date_any(str(nm["due"])) is None:
            errors.append("`next_milestone.due` invalid date format.")

    # report
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  - {w}")
        print()

    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print("✅ manifest.json validated successfully.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import json, datetime, sys
from pathlib import Path

def pct_badge(label, value):
    v = int(value)
    if v < 20: color = "orange"
    elif v < 40: color = "yellow"
    elif v < 60: color = "yellowgreen"
    elif v < 80: color = "green"
    else: color = "brightgreen"
    return f"![{label}](https://img.shields.io/badge/{label}-{v}%25-{color})"

def fmt_date(d):
    if not d: return "—"
    d = str(d).strip()
    try:
        if "/" in d:
            return datetime.datetime.strptime(d, "%d/%m/%Y").strftime("%d/%m/%Y")
        return datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return d

def render_focus(f):
    lines = []
    if f.get("current"): lines.append(f"- {f['current']} ✅")
    if f.get("next"):    lines.append(f"- Next: {f['next']}")
    if f.get("then"):    lines.append(f"- Then: {f['then']}")
    if f.get("security_prep_start"):
        lines.append(f"- Security+: prep starts {fmt_date(f['security_prep_start'])}")
    return "\n".join(lines) or "- Updating…"

def parse_milestones_flat(m):
    items = []
    for it in m.get("milestones", []) or []:  # <— changed key
        if not isinstance(it, dict): 
            continue
        due = it.get("due") or it.get("date")
        items.append({
            "id": it.get("id"),
            "title": it.get("title",""),
            "category": it.get("category",""),
            "status": (it.get("status") or "todo").lower(),
            "due_raw": due,
            "due_fmt": fmt_date(due) if due else "—",
            "repo": it.get("repo"),
        })
    return items

def _parse_date_any(d):
    if not d: return None
    for fmt in ("%d/%m/%Y","%Y-%m-%d"):
        try: return datetime.datetime.strptime(d, fmt)
        except Exception: pass
    return None

def pick_next_milestone(items):
    candidates = [x for x in items if x["status"] != "done" and _parse_date_any(x["due_raw"])]
    candidates.sort(key=lambda x: _parse_date_any(x["due_raw"]))
    return candidates[0] if candidates else None

def render_upcoming(items, limit=5):
    upcoming = [x for x in items if x["status"] != "done" and _parse_date_any(x["due_raw"])]
    upcoming.sort(key=lambda x: _parse_date_any(x["due_raw"]))
    out = []
    for it in upcoming[:limit]:
        repo = f" · `{it['repo']}`" if it["repo"] else ""
        out.append(f"- [ ] **{it['title']}** — {it['due_fmt']}{repo}")
    return "\n".join(out) or "_No upcoming milestones._"

def status_emoji(s):
    s = (s or "").lower()
    if "active" in s or "done" in s: return "✅ Active"
    if "scaffold" in s: return "🧩 Scaffolded"
    if "planned" in s: return "⏳ Planned"
    if "stub" in s: return "🔐 Stub"
    return s.title() or "—"

def render_roadmap_table(items):
    lines = []
    for it in items:
        status_icon = "✅ Done" if it["status"] == "done" else "⏳ In Progress" if it["status"] == "in_progress" else "⏳ Planned"
        lines.append(f"| {it['title']} | {it['category']} | {it['due_fmt']} | {status_icon} |")
    return "\n".join(lines)

def main():
    with open("manifest.json", encoding="utf-8") as f:
        m = json.load(f)

    # badges
    p = m.get("progress", {})
    badges = " ".join([
        pct_badge("Learning", p.get("learning", 0)),
        pct_badge("Projects", p.get("projects", 0)),
        pct_badge("Backend", p.get("backend", 0)),
        pct_badge("Flutter", p.get("flutter", 0)),
        pct_badge("Certifications", p.get("certifications", 0)),
    ])

    # focus + milestones
    items = parse_milestones_flat(m)
    focus_md = render_focus(m.get("focus", {}))
    next_m = m.get("next_milestone") or {}
    if not next_m:
        nm = pick_next_milestone(items)
        if nm:
            next_m = {"title": nm["title"], "due": nm["due_raw"], "id": nm["id"]}
    next_md = f"**{next_m.get('title','')}** — due **{fmt_date(next_m.get('due'))}** (`{next_m.get('id','')}`)" if next_m else "_None_"

    # repo table
    rows = []
    for r in m.get("repositories", []):
        topics = ", ".join((r.get("topics") or [])[:4]) or "—"
        target = fmt_date(r.get("target"))
        rows.append(
            f"| [`{r.get('name')}`]({r.get('url')}) | "
            f"{r.get('short_description') or r.get('description','—')} | "
            f"{topics} | {status_emoji(r.get('status'))} | {target} |"
        )
    repo_table = "\n".join([
        "| Repository | Description | Topics | Status | Target |",
        "|---|---|---|---|---|",
        *rows
    ])

    readme = f"""# AI + Cybersecurity Roadmap

{badges}

_Last updated: {fmt_date(m.get('updated'))}_

## 🧠 Current Focus
{focus_md}

## 🎯 Next Milestone
{next_md}

## 🗂️ Repository Overview

{repo_table}

## 🗓 Roadmap

| Milestone                    | Category              | Target Date | Status     |
| ---------------------------- | --------------------- | ----------- | ---------- |
{render_roadmap_table(items)}

---

Auto-generated from manifest.json
""".strip()

    with open("README.md","w", encoding="utf-8") as out:
        out.write(readme)

if __name__ == "__main__":
    main()

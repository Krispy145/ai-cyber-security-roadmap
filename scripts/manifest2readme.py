#!/usr/bin/env python3
import json, datetime

def fmt_date(d):
    if not d: return "—"
    d = str(d).strip()
    try:
        if "/" in d:
            return datetime.datetime.strptime(d, "%d/%m/%Y").strftime("%d/%m/%Y")
        return datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return d

def parse_milestones_flat(m):
    items = []
    for it in m.get("milestones", []) or []:
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

    items = parse_milestones_flat(m)

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

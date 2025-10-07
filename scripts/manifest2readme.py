#!/usr/bin/env python3
import json, datetime, pathlib

MANIFEST = pathlib.Path("manifest.json")
README = pathlib.Path("README.md")

def pct_badge(label, value):
    colors = [(0, "red"), (20, "orange"), (40, "yellow"), (60, "yellowgreen"), (80, "green"), (101, "brightgreen")]
    color = next(c for t, c in colors if value < t)
    return f"![{label}](https://img.shields.io/badge/{label}-{value}%25-{color})"

def fmt_date(d):
    if not d:
        return "—"
    d = d.strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(d, fmt).strftime("%d/%m/%Y")
        except:
            pass
    return d

def status_emoji(s):
    s = (s or "").lower()
    if "active" in s:
        return "✅ Active"
    if "scaffold" in s:
        return "🧩 Scaffolded"
    if "planned" in s:
        return "⏳ Planned"
    if "done" in s:
        return "🏁 Done"
    return s.title() if s else "—"

def main():
    m = json.loads(MANIFEST.read_text())
    progress = m.get("progress", {})
    badges = " ".join([pct_badge(k.title(), int(v)) for k, v in progress.items()])
    updated = m.get("updated") or datetime.date.today().strftime("%d/%m/%Y")

    repos = m.get("repositories", [])
    rows = ["| Repository | Description | Topics | Status | Target |", "|---|---|---|---|---|"]
    for r in repos:
        name = f"[`{r['name']}`]({r['url']})"
        desc = r.get("short_description") or r.get("description", "—")
        topics = ", ".join(r.get("topics", [])[:4]) or "—"
        stat = status_emoji(r.get("status"))
        tgt = fmt_date(r.get("target"))
        rows.append(f"| {name} | {desc} | {topics} | {stat} | {tgt} |")
    repo_table = "\n".join(rows)

    readme = f"""# AI + Cybersecurity Roadmap

{badges}

_Last updated: {fmt_date(updated)}_

## 🗂️ Repository Overview

{repo_table}

---
Auto-generated from manifest.json
"""
    README.write_text(readme)
    print("README.md regenerated from manifest.json")

if __name__ == "__main__":
    main()

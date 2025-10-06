#!/usr/bin/env python3
import json, datetime, pathlib

MANIFEST = pathlib.Path("manifest.json")
README   = pathlib.Path("README.md")

def pct_badge(label, value):
    # value expected 0..100 (int)
    colors = [
        (0, "red"),
        (20, "orange"),
        (40, "yellow"),
        (60, "yellowgreen"),
        (80, "green"),
        (101, "brightgreen"),
    ]
    color = next(c for t, c in colors if value < t)
    return f"![{label}](https://img.shields.io/badge/{label}-{value}%25-{color})"

def fmt_date(d):
    # Input may be "dd/mm/yyyy" or "yyyy-mm-dd" or None
    if not d:
        return "—"
    d = d.strip()
    try:
        # dd/mm/yyyy
        dt = datetime.datetime.strptime(d, "%d/%m/%Y")
    except ValueError:
        try:
            # yyyy-mm-dd
            dt = datetime.datetime.strptime(d, "%Y-%m-%d")
        except ValueError:
            return d
    return dt.strftime("%d/%m/%Y")

def status_emoji(s):
    s = (s or "").lower()
    if "done" in s or "active" in s:
        return "✅ " + s.title()
    if "scaffold" in s:
        return "🧩 " + s.title()
    if "stub" in s:
        return "🔐 " + s.title()
    if "planned" in s:
        return "⏳ " + s.title()
    return s.title() if s else "—"

def main():
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))

    # Progress badges (fallback to 0 if missing)
    progress = m.get("progress", {})
    learning        = int(progress.get("learning", 0))
    projects        = int(progress.get("projects", 0))
    backend         = int(progress.get("backend", 0))
    flutter         = int(progress.get("flutter", 0))
    certifications  = int(progress.get("certifications", 0))

    badges = " ".join([
        pct_badge("Learning", learning),
        pct_badge("Projects", projects),
        pct_badge("Backend", backend),
        pct_badge("Flutter", flutter),
        pct_badge("Certifications", certifications),
    ])

    updated = m.get("updated") or datetime.date.today().strftime("%d/%m/%Y")

    # Repositories table
    repos = m.get("repositories", [])
    # Expected fields: name, url (optional), status, target
    rows = []
    for r in repos:
        name = r.get("name", "")
        url  = r.get("url")
        link = f"[`{name}`]({url})" if url else f"`{name}`"
        desc = r.get("description", "")  # optional
        stat = status_emoji(r.get("status"))
        tgt  = fmt_date(r.get("target"))
        rows.append((link, desc, stat, tgt))

    # Build repo table markdown
    repo_md = []
    repo_md.append("| Repository | Description | Status | Target |")
    repo_md.append("|---|---|---|---|")
    for link, desc, stat, tgt in rows:
        repo_md.append(f"| {link} | {desc or '—'} | {stat} | {tgt} |")
    repo_table = "\n".join(repo_md)

    # Milestones by phase
    # manifest.milestones expected shape (flexible):
    # {
    #   "machine_learning": { "completed": [...], "pending": [...] },
    #   "ai_projects": { ... },
    #   ...
    # }
    ms = m.get("milestones", {})
    def bulletize(title_key, pretty_title):
        block = ms.get(title_key, {})
        comp = block.get("completed", [])
        pend = block.get("pending", [])
        lines = [f"### {pretty_title}"]
        for item in comp:
            if isinstance(item, dict):
                lines.append(f"- [x] {item.get('title','')} ({fmt_date(item.get('date'))})")
            else:
                lines.append(f"- [x] {item}")
        for item in pend:
            if isinstance(item, dict):
                due = item.get("due") or item.get("date")
                lines.append(f"- [ ] {item.get('title','')} ({fmt_date(due)})")
            else:
                lines.append(f"- [ ] {item}")
        return "\n".join(lines)

    milestone_blocks = [
        bulletize("machine_learning", "🎓 Machine Learning Foundations"),
        bulletize("ai_projects", "🤖 AI Engineering Projects"),
        bulletize("backend", "🧱 Backend Development"),
        bulletize("flutter", "🧩 Flutter App & Packages"),
        bulletize("security_plus", "🔐 Cybersecurity Learning"),
    ]
    milestones_md = "\n\n".join(milestone_blocks)

    # Current Focus (optional: from manifest.focus)
    focus = m.get("focus", {})
    focus_lines = []
    if focus:
        if "current" in focus:
            focus_lines.append(f"- {focus['current']} ✅")
        if "next" in focus:
            focus_lines.append(f"- Next: {focus['next']}")
        if "then" in focus:
            focus_lines.append(f"- Then: {focus['then']}")
        if "security_prep_start" in focus:
            focus_lines.append(f"- Security+: prep starts {fmt_date(focus['security_prep_start'])}")
    focus_md = "\n".join(focus_lines) if focus_lines else ""

    # Final README template
    readme = f"""# AI + Cybersecurity Roadmap

Public tracker of my transition into **AI Engineering with a Cybersecurity foundation**.  
This roadmap outlines my learning, certifications, and project milestones — all of which are reflected live on my portfolio site.

This repository also powers my **live Flutter CV**, where each milestone and repository card is dynamically rendered from the manifest below.

---

## 🧭 Progress Overview

{badges}

_Last updated: {fmt_date(updated)}_

---

## 🧠 Current Focus

{focus_md or "- Updating…"}

---

## 🗂️ Repository Overview

{repo_table}

---

## 🧩 Milestones

{milestones_md}

---

## 🧾 Live Data Manifest

This repository exposes a `manifest.json` that my Flutter portfolio uses to dynamically render progress, badges, and linked repos.

To integrate new sections or milestones, update the JSON accordingly and push the commit — my site will fetch and render it automatically.

---

## 🔗 Links

- 🌐 **Live CV:** <your-site>
- 🧰 **GitHub:** https://github.com/<your-username>
- 🧾 **Manifest:** [manifest.json](./manifest.json)

---

![Status](https://img.shields.io/badge/status-active-green)
![Updated](https://img.shields.io/badge/updated-{fmt_date(updated)}-informational)
"""
    README.write_text(readme, encoding="utf-8")
    print("README.md regenerated from manifest.json")

if __name__ == "__main__":
    main()

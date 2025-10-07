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
    # Accepts "dd/mm/yyyy" or "yyyy-mm-dd" or None → returns "dd/mm/yyyy"
    if not d:
        return "—"
    d = str(d).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            dt = datetime.datetime.strptime(d, fmt)
            return dt.strftime("%d/%m/%Y")
        except ValueError:
            continue
    return d  # leave as-is if unrecognized

def status_emoji(s):
    s = (s or "").lower()
    if "done" in s or "active" in s:
        return "✅ " + s.title()
    if "in_progress" in s or "progress" in s:
        return "🚀 In Progress"
    if "scaffold" in s:
        return "🧩 " + s.title()
    if "stub" in s:
        return "🔐 " + s.title()
    if "planned" in s or "todo" in s:
        return "⏳ " + s.title()
    return s.title() if s else "—"

def main():
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))

    # Progress badges
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

    # Updated date (manifest may store ISO or dd/mm/yyyy)
    updated_raw = m.get("updated") or datetime.date.today().strftime("%d/%m/%Y")
    updated = fmt_date(updated_raw)

    # Repositories table
    repos = m.get("repositories", [])
    rows = []
    for r in repos:
        name = r.get("name", "")
        url  = r.get("url")
        link = f"[`{name}`]({url})" if url else f"`{name}`"
        desc = r.get("description", "")  # optional
        stat = status_emoji(r.get("status"))
        tgt  = fmt_date(r.get("target"))
        rows.append((link, desc, stat, tgt))

    repo_md = ["| Repository | Description | Status | Target |", "|---|---|---|---|"]
    for link, desc, stat, tgt in rows:
        repo_md.append(f"| {link} | {desc or '—'} | {stat} | {tgt} |")
    repo_table = "\n".join(repo_md)

    # Milestones (flat → grouped by category)
    milestones = m.get("milestones_flat", [])
    categories = {}
    for item in milestones:
        cat = item.get("category", "Other")
        categories.setdefault(cat, []).append(item)

    order = {"done": 0, "in_progress": 1, "active": 1, "todo": 2, "planned": 2}

    milestone_blocks = []
    for cat, items in categories.items():
        # sort: done → in_progress/active → todo/planned, then by due/date ascending
        def sort_key(i):
            st = (i.get("status") or "").lower()
            rank = order.get(st, 3)
            # choose a date field for ordering
            d = i.get("due") or i.get("date")
            # convert to sortable value (YYYYMMDD) if parseable
            try:
                dd = fmt_date(d)
                y, mo, da = dd.split("/")[2], dd.split("/")[1], dd.split("/")[0]
                sortable = int(f"{y}{mo}{da}")
            except Exception:
                sortable = 99999999
            return (rank, sortable)

        items.sort(key=sort_key)

        lines = [f"### {cat}"]
        for it in items:
            title = it.get("title", "")
            st    = (it.get("status") or "").lower()
            date  = fmt_date(it.get("due") or it.get("date"))
            # emoji style for readability
            bullet = "✅" if st == "done" else ("🚀" if st in ("in_progress", "active") else "⏳")
            lines.append(f"- {bullet} {title} ({date})")
        milestone_blocks.append("\n".join(lines))

    milestones_md = "\n\n".join(milestone_blocks)

    # Current Focus (optional: from manifest.focus / next_milestone)
    focus = m.get("focus", {})
    focus_lines = []
    if "current" in focus:
        focus_lines.append(f"- {focus['current']} ✅")
    if "next" in focus:
        focus_lines.append(f"- Next: {focus['next']}")
    if "then" in focus:
        focus_lines.append(f"- Then: {focus['then']}")
    # also reflect next_milestone if present
    nm = m.get("next_milestone")
    if nm and isinstance(nm, dict):
        nm_title = nm.get("title")
        nm_due   = fmt_date(nm.get("due"))
        if nm_title:
            focus_lines.append(f"- Next milestone: **{nm_title}** → {nm_due}")
    # optional security prep date
    if "security_prep_start" in focus:
        focus_lines.append(f"- Security+: prep starts {fmt_date(focus['security_prep_start'])}")

    focus_md = "\n".join(focus_lines) if focus_lines else "- Updating…"

    # README content
    readme = f"""# AI + Cybersecurity Roadmap

Public tracker of my transition into **AI Engineering with a Cybersecurity foundation**.  
This roadmap outlines my learning, certifications, and project milestones — all of which are reflected live on my portfolio site.

This repository also powers my **live Flutter CV**, where each milestone and repository card is dynamically rendered from the manifest below.

---

## 🧭 Progress Overview

{badges}

_Last updated: {updated}_

---

## 🧠 Current Focus

{focus_md}

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
![Updated](https://img.shields.io/badge/updated-{updated}-informational)
"""
    README.write_text(readme, encoding="utf-8")
    print("README.md regenerated from manifest.json")

if __name__ == "__main__":
    main()

# SQL 50 Notebook

A MySQL study notebook for LeetCode's [Top SQL 50](https://leetcode.com/studyplan/top-sql-50/) study plan — one self-contained HTML page with a visual, step-by-step walkthrough of every problem, a revisit list and an interview-revision section.

**Hosted version:** https://claude.ai/artifact/WG3HhkQikzz7VevxHVrw7P

**Run locally:** download [`index.html`](index.html) and open it in any browser. No install, no server, works offline (it falls back to system fonts without internet).

## What's inside

All 50 problems in LeetCode's study-plan order, across seven topics: Select, Basic Joins, Basic Aggregate Functions, Sorting and Grouping, Advanced Select and Joins, Subqueries, and Advanced String Functions / Regex / Clause.

Each problem page has:

- **The task** in plain words, and the exact output columns.
- **Tables and sample data** with column types and primary keys. The sample rows are written to expose each problem's edge cases (NULLs, ties, duplicates, date boundaries).
- **How to solve it** — the reasoning as numbered steps.
- **Watch it run** — a stepper through real intermediate query results. Rows that survive a filter are highlighted, rows that get filtered out are struck through, groups are colour-banded and computed columns are tinted.
- **MySQL solution** with a copy button, plus the clauses it uses shown in MySQL's logical evaluation order.
- **Other ways to write it** — alternative solutions (window functions vs self joins, `NOT EXISTS` vs `LEFT JOIN … IS NULL`, and so on).
- **What to remember**, **traps**, and a **one-line recall cue**.
- **My notes** — a private notes box per problem.
- **Copy setup SQL** — `CREATE TABLE` + `INSERT` statements to reproduce the problem in your own MySQL 8.

Across the notebook:

- **Roadmap** — progress grid of all 50, filters by difficulty and status, "continue with" shortcut.
- **Revisit list** — star any problem; the list sorts by least recently reviewed and has a "Reviewed today" button.
- **Interview revision** — 16 patterns that cover all 50 problems, a MySQL function cheat sheet, 28 theory questions (WHERE vs HAVING, ranking functions, NULL semantics, indexes, isolation levels…), a flashcard drill (all 50, your revisit list, or one topic) and a checklist of last-minute traps.
- Light / dark theme, keyboard shortcuts, works on phones.

### Keyboard shortcuts

| Key | Action |
| --- | --- |
| `/` | Filter problems |
| `←` `→` | Step through a visualization (or flashcards in the drill) |
| `[` `]` | Previous / next problem |
| `Space` | Reveal a flashcard answer |

## Progress and backups

Solved marks, stars and notes are stored in your browser's `localStorage`, so they belong to the browser (and the file location or site) you use. Use **Export progress** in the sidebar to download a JSON backup, and **Import** to merge it back or move it to another browser. Export works when you open `index.html` locally; the hosted artifact viewer doesn't allow downloads.

## Accuracy

Every solution, alternative and visualization step was executed on **MySQL 8.0** against the sample data, and each alternative was checked to return the same result as the main solution. Problem statements are paraphrased, and sample data is original — LeetCode's own test data differs.

## Repository layout

```
index.html              the built notebook (open this)
build/
  content_a.py          problems 1–14   (Select, Basic Joins)
  content_b.py          problems 15–29  (Aggregates, Sorting and Grouping)
  content_c.py          problems 30–43  (Advanced Select and Joins, Subqueries)
  content_d.py          problems 44–50  (Strings / Regex / Clause)
  revision.py           sections, patterns, cheat sheet, theory Q&A, traps
  template.html         page layout, styles and app code
  build_data.py         runs every query on MySQL 8 → data.json
  build_html.py         template + data.json + revision → ../index.html
  data.json             query results (committed, so MySQL isn't needed to rebuild the page)
```

## Rebuilding

To change text, layout or revision content only (no database needed):

```bash
cd build
python3 build_html.py
```

To change a problem's SQL or sample data, re-run the queries first. This needs a MySQL 8 server; the script creates one scratch database per problem (`lc<id>`):

```bash
cd build
pip install -r requirements.txt
# default: root over the local Unix socket; or set MYSQL_HOST / MYSQL_PORT / MYSQL_USER / MYSQL_PASSWORD / MYSQL_SOCKET
python3 build_data.py      # fails loudly if any alternative disagrees with its main solution
python3 build_html.py
```

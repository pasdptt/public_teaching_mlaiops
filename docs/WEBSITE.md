# Publishing this repo as the course website

Two options. **Start with the first one** — it needs no configuration and is what students
will actually use.

---

## Option A — browse the repository directly (recommended)

Push the repo to GitHub and send students the URL of [`course/README.md`](../course/README.md).

GitHub renders Markdown, tables, and **Mermaid diagrams natively** in the repository view.
Nothing to configure, nothing to build, nothing to break the week before a session. The
same links work in a private repo for a closed cohort.

What students get:

| They want | They open |
|---|---|
| The syllabus | `course/README.md` |
| A lab handout | `course/labs/lab-0N-*.md` |
| The specification | `course/spec/course-specification.md` |
| The slides | `course/slides/course-deck.md` |
| The code | the repository root |

Set the repository description to the course code and pin `course/README.md` in the
README, so the landing page is obvious.

---

## Option B — GitHub Pages

Only worth it if you want a public URL that does not look like a code repository.

**The catch, and it is a real one.** GitHub renders Mermaid in Markdown files, but GitHub
Pages runs Jekyll, which does **not** render Mermaid by default. Jekyll emits the block as
`<pre><code class="language-mermaid">`, and the Mermaid script looks for `<pre class="mermaid">` —
so diagrams appear as raw text. Every diagram in this repo would break.

`_layouts/default.html` in this repo fixes it: it rewrites those blocks before initialising
Mermaid. That is the only non-obvious part of the setup.

**To enable:**

1. Settings → Pages → Source: *Deploy from a branch* → `main`, folder `/ (root)`
2. Confirm `_config.yml` and `_layouts/default.html` are committed
3. Wait for the build, then check that a page with a diagram actually renders one —
   [`course/labs/lab-04-cicd-monitoring-drift.md`](../course/labs/lab-04-cicd-monitoring-drift.md)
   has two and is the best page to test

`_config.yml` excludes `instructor/`, `src/`, `tests/`, and the rest of the code from the
published site. **Check that exclusion after your first build.** `instructor/` contains the
marking notes, which tell students exactly which judgement items carry the marks.

Excluding a directory from the *site* does not remove it from the *repository*. If the repo
is public, `instructor/` is still readable on github.com. For a public course site, keep
instructor material in a separate private repo.

---

## Keeping documents in sync

Two files are generated. Regenerate them rather than editing by hand:

```bash
python scripts/export_spec_md.py      # workbook  → course/spec/course-specification.md
node scripts/site/validate-mermaid.mjs # parse every diagram before pushing
```

The Excel workbook is authoritative for the specification; the Markdown is a rendering of
it. Edit the workbook, then re-export, or the website will quietly show stale marks.

The slide deck exists in two forms that do **not** generate from each other:

- `course/slides/course-deck.md` — Marp source, renders on GitHub with working diagrams
- `course/slides/ITCS355-course-deck.html` — the styled presentation deck

Change one, change the other, or delete the HTML if you would rather maintain a single file.
To present or export from the Markdown:

```bash
marp course/slides/course-deck.md -o deck.html      # presentable slides
marp course/slides/course-deck.md --pdf             # handout
```

---

## Diagram rules

Renderers disagree about HTML inside Mermaid labels. GitHub's repo view allows it; several
others — including Mermaid with `htmlLabels: false`, which some themes and exporters set —
render it as literal text, so a label reads `<b>Session 1</b>` instead of bold.

Keep diagram labels to these:

| Use | Not |
|---|---|
| `<br>` for line breaks — special-cased by Mermaid, safe everywhere | `<b>`, `<i>`, `<span>` |
| Plain words: `and`, `under`, `over` | `&amp;`, `&lt;`, `&gt;` |
| Quotes around any label containing punctuation | unquoted labels with `(`, `:`, `,` |

Emphasis belongs in the prose around the diagram, not inside a node.

## Validate before you push

CI runs the diagram check on every push (`.github/workflows/docs.yml`). A diagram that fails
to parse renders as raw text on the website, which is worse than having no diagram — and you
will not notice, because the failure is silent.

```bash
npm install mermaid jsdom
node scripts/site/validate-mermaid.mjs
```

All 12 diagrams in this repo currently parse against Mermaid's own grammar.

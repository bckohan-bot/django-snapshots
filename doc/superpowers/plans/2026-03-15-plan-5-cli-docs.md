# CLI Documentation Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add reference documentation for the four artifact protocol classes and the full `snapshots` management command hierarchy using `sphinxcontrib-typer` to auto-render CLI help from the live Typer app.

**Architecture:** Install `sphinxcontrib-typer`, register it in `conf.py` after `sphinxcontrib_django` (which handles `django.setup()`), then create four new RST pages under `doc/source/reference/` and wire them into the existing toctree. The core commands page uses the class-level `Command.typer_app`; the export/import pages use the standalone Typer group objects from their plugin modules.

**Tech Stack:** Sphinx, sphinxcontrib-typer, sphinxcontrib-django, sphinx autodoc, RST

---

## Chunk 1: Infrastructure and Protocols Page

### Task 1: Add sphinxcontrib-typer dependency and register extension

**Files:**
- Modify: `pyproject.toml` (dependency-groups.docs section)
- Modify: `doc/source/conf.py` (extensions list)

**Context:** The `docs` dependency group is in `pyproject.toml` under `[dependency-groups]`. The `conf.py` extensions list currently ends with `"sphinx.ext.viewcode"`. `sphinxcontrib.typer` MUST come after `sphinxcontrib_django` (which calls `django.setup()`) so Django is initialized before any `.. typer::` directive runs. The underscore in `sphinxcontrib_django` is intentional — do not normalize the naming style.

- [ ] **Step 1: Add sphinxcontrib-typer to pyproject.toml**

In `pyproject.toml`, find the `docs` group under `[dependency-groups]` and add `sphinxcontrib-typer` (use `>=0.5.0` as a floor — pick whatever is current on PyPI):

```toml
docs = [
    "doc8>=1.1.2",
    "furo>=2024.8.6",
    "readme-renderer[md]>=44.0",
    "sphinx>=8.0.0",
    "sphinx-autobuild>=2024.10.3",
    "sphinx-tabs>=3.4.7",
    "sphinxcontrib-django>=2.5",
    "sphinxcontrib-typer[pdf,html]>=0.8.0",
]
```

- [ ] **Step 2: Install the new dependency**

```bash
uv sync --group docs
```

Expected: resolves and installs `sphinxcontrib-typer` and its dependencies with no errors.

- [ ] **Step 3: Register extension in conf.py**

In `doc/source/conf.py`, add `"sphinxcontrib.typer"` to the end of the extensions list:

```python
extensions = [
    "sphinxcontrib_django",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx_tabs.tabs",
    "sphinx.ext.viewcode",
    "sphinxcontrib.typer",
]
```

- [ ] **Step 4: Verify docs build still passes**

```bash
just docs
```

Expected: build completes with zero errors. (There may be a warning about `protocols`, `commands/index` not being in any toctree — that is resolved in later tasks.) If there are errors related to `sphinxcontrib.typer` itself, check that the package installed correctly.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml doc/source/conf.py uv.lock
git commit -m "feat(docs): add sphinxcontrib-typer dependency and register extension"
```

---

### Task 2: Create protocols reference page

**Files:**
- Create: `doc/source/reference/protocols.rst`

**Context:** The four public protocol classes live in `django_snapshots.artifacts.protocols`. Their annotations (`artifact_type`, `filename`, `metadata` for exporters; `artifact_type` for importers) are defined on the base classes (`ArtifactExporterBase`, `ArtifactImporterBase`) and will surface via `:show-inheritance:`. Do NOT document `ArtifactExporterBase` or `ArtifactImporterBase` directly — they are internal helpers. Follow the style of `doc/source/reference/dataclasses.rst`: `.. include:: ../refs.rst`, a label, a title underlined with `=`, a brief intro paragraph, then one `.. autoclass::` block per class.

- [ ] **Step 1: Create protocols.rst**

Create `doc/source/reference/protocols.rst` with this content:

```rst
.. include:: ../refs.rst

.. _reference-protocols:

=========
Protocols
=========

These runtime-checkable :class:`~typing.Protocol` classes define the interfaces
that custom artifact exporters and importers must satisfy. Use them with
:func:`isinstance` to verify conformance at runtime.

ArtifactExporter
----------------

.. autoclass:: django_snapshots.artifacts.protocols.ArtifactExporter
   :members:
   :show-inheritance:

AsyncArtifactExporter
---------------------

.. autoclass:: django_snapshots.artifacts.protocols.AsyncArtifactExporter
   :members:
   :show-inheritance:

ArtifactImporter
----------------

.. autoclass:: django_snapshots.artifacts.protocols.ArtifactImporter
   :members:
   :show-inheritance:

AsyncArtifactImporter
---------------------

.. autoclass:: django_snapshots.artifacts.protocols.AsyncArtifactImporter
   :members:
   :show-inheritance:
```

- [ ] **Step 2: Verify the page builds (standalone check)**

```bash
just docs
```

Expected: build completes. Sphinx will warn that `protocols` is not included in any toctree — that warning is expected and will be resolved in Task 4. There should be no autodoc errors for the four protocol classes.

- [ ] **Step 3: Commit**

```bash
git add doc/source/reference/protocols.rst
git commit -m "feat(docs): add protocols reference page"
```

---

## Chunk 2: Command Pages and Wire-Up

### Task 3: Create commands/ directory and all three command pages

**Files:**
- Create: `doc/source/reference/commands/index.rst`
- Create: `doc/source/reference/commands/export.rst`
- Create: `doc/source/reference/commands/import.rst`

**Context:**

**Critical — Typer app access paths:**
- Core commands page: target is `django_snapshots.management.commands.snapshots.Command.typer_app` — this is the *class-level* attribute, which contains exactly the five core commands (list, delete, info, prune, check). The export/import groups are only on the per-*instance* app and do NOT appear here.
- Export page: target is `django_snapshots.export.management.plugins.snapshots.export` — this is a `django_typer.management.Typer` instance (confirmed), not a plain function.
- Import page: target is `django_snapshots.import.management.plugins.snapshots.import_cmd` — also a `django_typer.management.Typer` instance. The module name `import` is a Python reserved word; `sphinxcontrib-typer` resolves this path via `importlib` so the reserved word is not an issue.

**`:prog:` option** sets the command name shown in help output. Use `manage.py snapshots`, `manage.py snapshots export`, and `manage.py snapshots import` respectively.

**`:make-sections:`** renders each subcommand as its own RST section heading.

`commands/index.rst` must contain a hidden toctree pointing to `export` and `import` so Sphinx includes those pages in the doc tree (even though they are not listed in the visible navigation on this page).

- [ ] **Step 1: Create commands/index.rst**

Create `doc/source/reference/commands/index.rst`:

```rst
.. include:: ../../refs.rst

.. _reference-commands:

========
Commands
========

Reference for all ``manage.py snapshots`` subcommands.

Core Commands
-------------

.. typer:: django_snapshots.management.commands.snapshots.Command.typer_app
   :prog: manage.py snapshots
   :make-sections:

.. toctree::
   :hidden:

   export
   import
```

- [ ] **Step 2: Create commands/export.rst**

Create `doc/source/reference/commands/export.rst`:

```rst
.. include:: ../../refs.rst

.. _reference-commands-export:

======
Export
======

Reference for the ``manage.py snapshots export`` subcommands.

.. typer:: django_snapshots.export.management.plugins.snapshots.export
   :prog: manage.py snapshots export
   :make-sections:
```

- [ ] **Step 3: Create commands/import.rst**

Create `doc/source/reference/commands/import.rst`:

```rst
.. include:: ../../refs.rst

.. _reference-commands-import:

======
Import
======

Reference for the ``manage.py snapshots import`` subcommands.

.. typer:: django_snapshots.import.management.plugins.snapshots.import_cmd
   :prog: manage.py snapshots import
   :make-sections:
```

- [ ] **Step 4: Verify the three pages build**

```bash
just docs
```

Expected: build completes. Sphinx will warn that `commands/index` is not in any toctree — that will be resolved in Task 4. There must be no errors from the `.. typer::` directives. If you see `ModuleNotFoundError` or `AttributeError`, double-check the access paths above.

- [ ] **Step 5: Commit**

```bash
git add doc/source/reference/commands/
git commit -m "feat(docs): add command reference pages (core, export, import)"
```

---

### Task 4: Wire new pages into reference/index.rst and verify full build

**Files:**
- Modify: `doc/source/reference/index.rst`

**Context:** The current toctree in `doc/source/reference/index.rst` has five entries: `settings`, `dataclasses`, `storage`, `connectors`, `exceptions`. Add `protocols` after `dataclasses` and `commands/index` at the end. The exact final toctree is specified below — replace the entire toctree block.

`commands/export` and `commands/import` are reachable via the hidden toctree inside `commands/index.rst` — they do NOT need entries in `reference/index.rst`.

- [ ] **Step 1: Update reference/index.rst toctree**

In `doc/source/reference/index.rst`, replace the toctree block so the file reads:

```rst
.. include:: ../refs.rst

.. _reference:

=========
Reference
=========

Complete API reference for django-snapshots.

.. toctree::
   :maxdepth: 1
   :caption: Reference:

   settings
   dataclasses
   protocols
   storage
   connectors
   exceptions
   commands/index
```

- [ ] **Step 2: Run full docs build and verify zero errors**

```bash
just docs
```

Expected output: build completes with **zero errors and zero warnings** (no "document isn't included in any toctree" warnings). If there are warnings about missing toctree entries or directive failures, fix them before committing.

- [ ] **Step 3: Spot-check rendered output**

Open the built docs (`doc/_build/html/reference/index.html` or whatever `just docs` outputs) and confirm:

1. `reference/protocols.html` renders all four protocol classes with method signatures.
2. `reference/commands/index.html` shows the five core commands (list, delete, info, prune, check).
3. `reference/commands/export.html` shows the three export subcommands (database, media, environment).
4. `reference/commands/import.html` shows the three import subcommands (database, media, environment).
5. Navigation links from `reference/index` reach `protocols` and `commands/index` directly; `commands/export` and `commands/import` are reachable from `commands/index`.

- [ ] **Step 4: Commit**

```bash
git add doc/source/reference/index.rst
git commit -m "feat(docs): wire protocols and commands pages into reference index"
```

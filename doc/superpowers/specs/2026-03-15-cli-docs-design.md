# CLI Documentation Design Spec

**Date:** 2026-03-15
**Feature:** Reference documentation for artifact protocols and management commands

---

## Goal

Add API reference documentation for the four artifact protocol classes and the full `snapshots` management command hierarchy (core commands, export group, import group) using `sphinxcontrib-typer` to render CLI help automatically from the live Typer app.

---

## Architecture

### Infrastructure Changes

1. **Add `sphinxcontrib-typer`** to `pyproject.toml` under the `docs` dependency group.
2. **Add `"sphinxcontrib.typer"`** to the `extensions` list in `doc/source/conf.py`, **after** `"sphinxcontrib_django"`. The `sphinxcontrib_django` extension calls `django.setup()` during its Sphinx setup hook. `sphinxcontrib.typer` must be listed after it so Django is initialized before any `.. typer::` directive resolves Python paths. The `DJANGO_SETTINGS_MODULE` environment variable is already set in `conf.py` to `"tests.settings"`, ensuring the full app registry (including export/import plugin groups) is loaded.

   **Naming convention note:** `sphinxcontrib_django` uses an underscore in the extension name (this is intentional and must be preserved). `sphinxcontrib.typer` uses a dot. Both forms are valid Sphinx extension identifiers — do not normalize them to a single style.

### New Files

```
doc/source/reference/
├── protocols.rst        — autoclass docs for the four artifact protocol classes
└── commands/
    ├── index.rst        — core snapshots command (list/delete/info/prune/check)
    ├── export.rst       — export group (database/media/environment subcommands)
    └── import.rst       — import group (database/media/environment subcommands)
```

### Modified Files

- `doc/source/reference/index.rst` — add `protocols` and `commands/index` to the toctree
- `doc/source/conf.py` — add `"sphinxcontrib.typer"` to `extensions`
- `pyproject.toml` — add `sphinxcontrib-typer` to the `docs` dependency group

---

## Typer App Access Paths

**Key fact:** `Command.typer_app` at the *class level* contains only the five core commands (list, delete, info, prune, check). The export/import groups are attached to a per-*instance* `typer_app` by `AppConfig.ready()` and are not present on the class attribute. Therefore, each page uses a different Typer app object:

| Page | Directive target | `--prog` |
|------|-----------------|----------|
| `commands/index.rst` | `django_snapshots.management.commands.snapshots.Command.typer_app` | `manage.py snapshots` |
| `commands/export.rst` | `django_snapshots.export.management.plugins.snapshots.export` | `manage.py snapshots export` |
| `commands/import.rst` | `django_snapshots.import.management.plugins.snapshots.import_cmd` | `manage.py snapshots import` |

Note: the import plugin module uses the name `import_cmd` (not `import`) because `import` is a Python reserved word. The dotted path `django_snapshots.import.management.plugins.snapshots.import_cmd` is valid for `sphinxcontrib-typer` because it resolves via `importlib`, not the `import` statement. Both `export` and `import_cmd` are confirmed `django_typer.management.Typer` instances (not bare decorated functions) — verified by `python -c "... print(type(export))"` which returned `<class 'django_typer.management.Typer'>` for both. They are valid `.. typer::` targets.

---

## Component Details

### `protocols.rst`

Documents four `@runtime_checkable Protocol` classes from `django_snapshots.artifacts.protocols`:

- `ArtifactExporter` — synchronous exporter protocol (`generate(dest: Path) -> None`)
- `AsyncArtifactExporter` — async exporter protocol (`async generate(dest: Path) -> None`)
- `ArtifactImporter` — synchronous importer protocol (`restore(src: Path) -> None`)
- `AsyncArtifactImporter` — async importer protocol (`async restore(src: Path) -> None`)

**Out of scope for this page:** `ArtifactExporterBase` and `ArtifactImporterBase` also exist in the module. They are abstract base classes used internally for protocol inheritance and are not part of the public integration surface. They are deliberately excluded from this reference page.

Uses `.. autoclass:: django_snapshots.artifacts.protocols.<ClassName>` with `:members:` and `:show-inheritance:` for each of the four public protocol classes.

### `commands/index.rst`

Documents the root `snapshots` command and its five core subcommands. Uses the class-level `Command.typer_app`, which contains exactly the five core commands:

```rst
.. typer:: django_snapshots.management.commands.snapshots.Command.typer_app
   :prog: manage.py snapshots
   :make-sections:
```

This page also contains a toctree linking `export` and `import` (so that Sphinx includes them in the documentation tree):

```rst
.. toctree::
   :hidden:

   export
   import
```

### `commands/export.rst`

Documents the export group and its three subcommands (`database`, `media`, `environment`):

```rst
.. typer:: django_snapshots.export.management.plugins.snapshots.export
   :prog: manage.py snapshots export
   :make-sections:
```

### `commands/import.rst`

Documents the import group and its three subcommands (`database`, `media`, `environment`):

```rst
.. typer:: django_snapshots.import.management.plugins.snapshots.import_cmd
   :prog: manage.py snapshots import
   :make-sections:
```

### `reference/index.rst` Update

The existing toctree has five entries: `settings`, `dataclasses`, `storage`, `connectors`, `exceptions`. Two new entries are added: `protocols` (after `dataclasses`) and `commands/index` (at the end).

Final toctree after modification (exact order):

```rst
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

`protocols` is inserted after `dataclasses` (both describe data/type contracts). `commands/index` is last (CLI-facing, separate concern from the Python API entries above it).

---

## Testing / Verification

After implementation, run:

```bash
just docs
```

The build must complete with zero warnings or errors related to the new pages. Verify:

1. `reference/protocols` page renders all four protocol classes with their method signatures.
2. `reference/commands/index` page shows help for `list`, `delete`, `info`, `prune`, and `check`.
3. `reference/commands/export` page shows help for `database`, `media`, and `environment` export subcommands.
4. `reference/commands/import` page shows help for `database`, `media`, and `environment` import subcommands.
5. All four new pages are reachable: `protocols` and `commands/index` are direct children of `reference/index`; `commands/export` and `commands/import` are reachable via the hidden toctree in `commands/index.rst` (not directly from `reference/index`).

---

## Notes

- **Django lazy strings:** Command help strings use `_()` (`gettext_lazy`). `sphinxcontrib-typer` renders help by executing the CLI, which calls `str()` on lazy strings automatically. No workaround is needed.
- **Attribute asymmetry in protocols:** `ArtifactExporterBase` annotates `artifact_type`, `filename`, and `metadata`; `ArtifactImporterBase` annotates only `artifact_type`. The annotations live on the base classes and will be pulled into autodoc output via `:show-inheritance:`.

## Out of Scope

- Tutorial or how-to content for the commands (Diátaxis: belongs in tutorials/how-to sections).
- Documenting internal command implementation details (only the CLI interface is documented here).
- Documenting `ArtifactExporterBase` and `ArtifactImporterBase` (internal protocol inheritance helpers, not part of the public integration surface).
- Cross-references from command docs to protocol docs (can be added in a follow-up).

# django-app-template

This is my template for Django apps (*not Django sites!*), based on the tooling and workflow patterns from:
   
   * [django-enum](https://github.com/django-commons/django-enum)
   * [django-typer](https://github.com/django-commons/django-typer)

The top level goals for this repository organization are to:

   * Test adequate permutations of currently supported versions of Python/Django
   * Support development on Linux/OSX/Windows
   * Have secure release processes
   * Encourage rigorous and linked documentation

Key features and design choices, include:

   * Toolchain:
      * [uv](https://docs.astral.sh/uv/)
      * [ruff](https://docs.astral.sh/ruff/)
      * [pytest](https://pytest.org/)
      * [just](https://just.systems/)
      * [pre-commit](https://pre-commit.com/)
      * [mypy](https://mypy-lang.org/) & [pyright](https://github.com/microsoft/pyright)
      * [Sphinx](https://www.sphinx-doc.org/) & [Furo](https://pradyunsg.me/furo/)
      * [doc8](https://github.com/PyCQA/doc8)
      * [zizmor](https://woodruffw.github.io/zizmor/)
      * [bandit](https://bandit.readthedocs.io/)
      * [ReadTheDocs](https://readthedocs.org)
      
   * We do not use tox or nox. CI matrix permutations are tested using uv with dependency    groups and just recipe shortcuts. For example to run all tests against python 3.13 and Django 5.2:

      ``just test-all -p 3.13 --group dj52``
   * The bootstrap workflow is configurable to run tests against just sqlite or all Django supported RDBMS.
   * Release workflow is triggered on tag creation with semver naming patterns - it uses trusted publishing with PyPi.
   * Testing
      * In CI a pip freeze artifact is created for each test run
      * A ``just debug-test <test>`` recipe drops you into the debugger at the start of a test. If the test is a ``ui`` test and you have elected to use playwright a browser will open in headed mode.
   * Configurable options include:
      * Database testing strategy (sqlite or all)
      * Use [Django Commons](https://github.com/django-commons/membership) [Code of Conduct](https://github.com/django-commons/membership/blob/main/CODE_OF_CONDUCT.md).
      * Use [OpenSSF Scorecard](https://securityscorecards.dev/)
      * License: MIT, Apache, BSD-3 or None
      * Use playwright for UI testing

## Using This Template

### On GitHub (recommended)

**Prerequisite:** Create a [fine-grained PAT](https://github.com/settings/personal-access-tokens/new)
scoped to the new repo with **Contents**, **Pull requests**, and **Workflows** set to
**Read and write**, then add it as a repo secret named **`BOOTSTRAP_TOKEN`**.
GitHub's default `GITHUB_TOKEN` cannot push `.github/workflows/` files, so the bootstrap PR
will fail without this token.

1. Click **"Use this template"** → **"Create a new repository"**
2. Create a [fine-grained PAT](https://github.com/settings/personal-access-tokens/new)
   scoped to the new repo with **Contents**, **Pull requests**, and **Workflows** set to
   **Read and write**. We recommend setting the expiry time to as short as possible because this token will be one-time use by the boostrap workflow.
   ![Multiple Subcommands Example](https://raw.githubusercontent.com/bckohan/django-app-template/main/PAT_perms.png)
2. Add the `BOOTSTRAP_TOKEN` secret (Settings → Secrets and variables → Actions).
3. Create third party secrets:
   * Create a [codecov.io](https://codecov.io) key and set it as the ``CODECOV_TOKEN`` in an environment named ``codecov``
   * (If using) Create a [scorecard PAT](https://github.com/ossf/scorecard-action/blob/main/docs/authentication/fine-grained-auth-token.md) and assign it to ``SCORECARD_TOKEN`` in an environment named ``scorecard``
4. Run the **Bootstrap** workflow manually (Actions → Bootstrap Repository → Run workflow).
   It reads the repo name, owner, and description from GitHub's metadata and opens a PR
   with all template files rendered.
   * **Choose your test strategy** - By default tests will run against SQLite only. To run tests against all Django-supported RDBMS, check the **database tests** box.
   * **Choose your Code of Conduct** - By default no Code of Conduct is included. Check the **Django Commons Code of Conduct** box to include `CODE_OF_CONDUCT.md` and the `update_coc.yml` workflow that keeps it synced with [django-commons](https://github.com/django-commons/membership).
5. Review and merge the PR.

### Locally

```bash
uvx --with pyfiglet --with jinja2-time cookiecutter gh:bckohan/django-app-template
```

## Derived Variables

All values are derived automatically from GitHub repository metadata — no manual input needed:

| Variable | Source |
|----------|--------|
| `project_slug` | repository name |
| `package_name` | repository name with `-` → `_` |
| `description` | repository description |
| `author_name` | owner's GitHub display name |
| `author_email` | owner's public GitHub email (falls back to `@users.noreply.github.com`) |
| `github_owner` | repository owner (org or user) |
| `year` | current year |

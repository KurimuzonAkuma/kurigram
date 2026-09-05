# Contributing to Kurigram

Thanks for taking the time to contribute! This document covers how to set up a development
environment, the expected workflow, and what we look for in a pull request.

## Getting started

Kurigram requires Python >=3.9. Dependency and virtual environment management is done via
[`uv`](https://docs.astral.sh/uv/).

```bash
uv sync --extra dev
```

This installs the package together with its development dependencies (linting, type checking,
testing). Avoid `uv pip` (a deprecated interface) and avoid a plain `uv sync` when you only need
the `dev` extra, since pulling in the `docs` extra can fail dependency resolution unrelated to
your change.

Alternatively, a pip-based `venv` workflow is available through `make`:

```bash
make venv-dev
```

### Generated code

`pyrogram/raw/{types,functions,base,all.py}` and `pyrogram/errors/exceptions/` are generated from
TL schema files and are not tracked in git. Run the generator once before working on anything that
touches type checking or code that imports from `pyrogram.raw`:

```bash
make api
```

Never hand-edit files under these paths. If a change appears to require editing generated code,
the actual fix belongs in the compiler/templates under `compiler/`, or in the code that consumes
the generated types.

## Development workflow

Run these before opening a pull request:

```bash
make lint         # ruff check
make typecheck     # ty check (requires `make api` to have been run first)
make test-unit     # fast unit suite, no live credentials needed
```

`make test` runs the full suite, including integration tests that require live Telegram
credentials in a git-ignored `.env.test` file; these are skipped automatically when the file is
absent. Prefer `tests/unit` for anything that doesn't require a live connection.

New tests belong under either `tests/unit/` or `tests/integrations/`: the directory a test file
lives in determines whether it's collected as a unit or integration test, so pick the tree that
matches what your test actually needs.

### Optional: pre-commit hook

The repository ships a `pre-commit` config that runs `make lint` and `make typecheck` on commit:

```bash
pre-commit install
```

### Linting and type checking policy

`ruff`'s selected rule set and `ty`'s rule overrides in `pyproject.toml` are both intentionally
narrower than "everything the tool can check": they're expanded incrementally, one rule at a
time, as the codebase is brought into compliance with it. When contributing:

- Don't widen an ignored `ty` rule or narrow the `ruff` rule set just to make a change pass.
- Fix the underlying issue instead.
- Don't make unrelated style changes to code outside the rules already enforced; keep pull
  requests focused on their stated purpose.

## Code style conventions

A few conventions that have come up repeatedly in code review but aren't enforced by `ruff` or
`ty`, so they're written down here instead:

- **No `assert` for runtime guards in library code.** `assert` statements are stripped when
  Python runs with `-O`, and raise a bare `AssertionError` with no context for library consumers.
  Raise `RuntimeError` (or a more specific exception) instead.
- **When raising with a message, assign it to a variable first**, then raise it, rather than
  writing the message inline in the `raise` statement:

  ```python
  msg = f"connection not open (state={self._state})"
  raise RuntimeError(msg)
  ```

- **All code references in comments use backticks**: `` `Client.method()` ``, not
  `Client.method()`. This applies throughout the comment, not just the first reference.
- **No em dashes or `--` as punctuation in comments.** Use a comma, colon, parentheses, or a
  single `-` instead. This includes `# ty: ignore[rule] - reason` comments: the `[rule]` bracket
  syntax is the part `ty` actually specifies, but the trailing `- reason` is our own convention for
  explaining *why* the ignore is there, so reviewers and future readers don't have to reconstruct
  the context from scratch.
- **A parameter that needs to distinguish "not passed" from a meaningful `None`** (for example,
  a `reply_markup` parameter where `None` means "remove the markup") should default to the
  `object` class itself (not an instance of it) as the "not specified" sentinel, keeping `None`
  free to carry its own meaning. Check for existing uses of this pattern elsewhere in the method
  or type before introducing a new one.
- **Test doubles that stand in for `Client`** are named `FakeClient`, not `Client` or `TestClient`
  (pytest warns about `Test*` classes that define `__init__`). This is an existing pattern across
  the test suite: reuse it rather than inventing a new name per test file.
- **Module-level constants that never change** should be annotated `Final`.
- **An optional third-party import** (a package the project doesn't depend on, used defensively
  behind a feature that needs it) should be marked `# ty: ignore[unresolved-import]` with a short
  comment noting that it's optional and not a project dependency, linking to the relevant section
  of the [docs](https://docs.kurigram.icu) if one covers that optional feature.

## Commit and pull request guidelines

- Write commit messages using [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat: ...`, `fix(scope): ...`, `chore(scope): ...`, `docs: ...`, etc.), matching the existing
  git history.
- **The pull request title matters, not just commit messages.** The project squash-merges, so
  the PR title becomes the actual commit message on `dev`. Title it the same way you would a
  commit: `type(scope): description`, describing what the change actually does rather than a
  generic label. If the branch gains more commits or changes scope before merge, update the title
  to match; don't leave it describing an earlier, narrower version of the change.
- Keep pull requests focused on one logical change. Unrelated fixes should be separate PRs.
- Reference any related issue in the pull request description.

### Before submitting, make sure that

- [ ] `make lint` passes
- [ ] `make typecheck` passes (after `make api`)
- [ ] `make test-unit` passes
- [ ] Tests were added or updated for behavioral changes
- [ ] The commit message(s) follow Conventional Commits

## Questions

If something is unclear, reach out on the [official chat](https://t.me/kurigram_chat) or follow
news and announcements on the [official channel](https://t.me/kurigram_news).

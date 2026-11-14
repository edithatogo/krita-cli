# Contributing to krita-cli

Contributions improve the Krita desktop plugin, Python client, command-line interface, and MCP server. Explain which surfaces are affected and preserve their documented parity and security boundaries.

## Before you start

Read the [README](README.md), [package configuration](pyproject.toml), and [CI workflow](.github/workflows/ci.yml). Keep plugin behavior, API types, client behavior, and command documentation consistent when changing a shared operation.

Search existing issues and pull requests to avoid duplicating work. Describe substantial proposals before implementation, and use repository issue or pull request templates when available. Small corrections can go directly into a focused pull request.

For bug reports, include the affected version or commit, environment, minimal reproduction, expected and actual behavior, and sanitized diagnostics. For feature requests, explain the use case and intended outcome.

## Development and validation

Use the supported Python version and locked environment. Existing CI commands include:

```sh
uv sync --frozen
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run ty check src/ types/
uv run pytest tests/ -v --cov=src --cov-fail-under=95
```

Preserve the configured lint, type, and coverage gates. The README also documents `uv run pytest tests/e2e/test_e2e_mock.py` for checks without Krita. Separate mock-based results from desktop integration evidence. For live plugin checks, use a disposable document and record Krita, operating-system, and plugin versions; confirm restart and plugin installation where required. Cover malformed requests and relevant path or resource limits when changing tool behavior.

Update affected documentation and examples alongside behavior changes. Add a focused regression case for a bug fix where executable tests are appropriate. Record checks that were not run and the reason.

## Submitting a pull request

Create a focused branch from the current `master` branch and open a pull request back to it. Keep unrelated formatting, refactoring, and dependency changes separate.

Include:

- The problem, proposed change, and resulting behavior.
- Related issues or existing track references.
- Exact validation commands or inspection steps, results, and limitations.
- Compatibility implications and any data or dependency provenance.

Inspect the complete diff before submission. Required automated checks must pass before merge. Follow the existing repository and account policies; this guide does not introduce a second-person approval requirement or relax existing checks.

## Security and sensitive information

Follow the [account security policy](https://github.com/edithatogo/.github/blob/main/SECURITY.md). Report vulnerabilities privately through GitHub's **Report a vulnerability** option if available. Otherwise request a private reporting contact without disclosing the vulnerability publicly. Keep credentials, personal data, and unredacted logs out of commits, issues, and examples.

## Licensing and conduct

Respect the [existing license](LICENSE) and preserve third-party notices. Submit only material you are entitled to contribute, and document unclear permissions before adding third-party content. Follow the [account code of conduct](https://github.com/edithatogo/.github/blob/main/CODE_OF_CONDUCT.md). This guide adds no CLA, mandatory sign-off, or relicensing condition.

## Reference guidance

- [GitHub contributor guidelines](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors)
- [OpenSSF Best Practices criteria](https://www.bestpractices.dev/en/criteria)

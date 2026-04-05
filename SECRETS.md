# Required Repository Secrets

The following secrets must be configured in GitHub → Settings → Secrets and variables → Actions:

| Secret | Description | How to Create |
|--------|-------------|---------------|
| `GH_TOKEN` | GitHub Personal Access Token with `repo` scope | GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens |
| `PYPI_TOKEN` | PyPI API token for publishing packages | https://pypi.org/manage/account/token/ → Create token |

## Creating GH_TOKEN

1. Go to https://github.com/settings/tokens
2. Create a fine-grained token with:
   - Repository access: This repository only
   - Permissions: Contents (read/write), Pull requests (read/write), Workflows (read/write)
3. Copy the token and add it as `GH_TOKEN` in repo secrets

## Creating PYPI_TOKEN

1. Go to https://pypi.org/manage/account/
2. Scroll to "API tokens" section
3. Click "Add API token"
4. Set scope to "Entire account" or "Specific project" (if krita-cli exists)
5. Copy the token and add it as `PYPI_TOKEN` in repo secrets

## Verifying Secrets

After adding secrets, the CI release workflow will use them automatically when pushing to master with a conventional commit that triggers a release.

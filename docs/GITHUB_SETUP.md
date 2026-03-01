# GitHub Repository Setup Guide

This guide helps you configure your GitHub repository for optimal CI/CD and collaboration.

## Branch Protection (Recommended)

Protect your main branch from accidental force pushes and ensure code quality.

### Steps to Enable Branch Protection:

1. Go to your repository on GitHub
2. Click **Settings** → **Branches**
3. Click **Add rule** under "Branch protection rules"
4. Configure the following:

#### Branch name pattern:
```
main
```

#### Recommended Settings:

✅ **Require a pull request before merging**
- Require approvals: 1 (if working with a team)
- Dismiss stale pull request approvals when new commits are pushed

✅ **Require status checks to pass before merging**
- Require branches to be up to date before merging
- Status checks that are required:
  - `test (3.10)` - Python 3.10 tests
  - `test (3.11)` - Python 3.11 tests
  - `test (3.12)` - Python 3.12 tests
  - `lint` - Code linting
  - `validate` - PR validation

✅ **Require conversation resolution before merging**
- All PR comments must be resolved

⚠️ **Do NOT require signed commits** (unless you have GPG set up)

⚠️ **Do NOT include administrators** (if you're the only developer)
- This allows you to push directly when needed

✅ **Allow force pushes** → **Specify who can force push**
- Select: Administrators only

✅ **Allow deletions** → Disabled

5. Click **Create** or **Save changes**

---

## GitHub Actions Permissions

Ensure GitHub Actions has proper permissions:

1. Go to **Settings** → **Actions** → **General**
2. Under "Workflow permissions":
   - Select: **Read and write permissions**
   - ✅ Check: **Allow GitHub Actions to create and approve pull requests**
3. Click **Save**

---

## Secrets Configuration

If you need to run integration tests with Discord:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add the following (if needed):

### Optional Secrets:

- `DISCORD_TOKEN` - Bot token for integration tests (only if testing live bot)
- `TEST_GUILD_ID` - Test server ID for integration tests
- `TEST_CHANNEL_ID` - Test channel ID for integration tests

**Note:** Current tests don't require these secrets as they test bot logic without connecting to Discord.

---

## Dependabot Configuration

Dependabot is already configured in `.github/dependabot.yml`.

To manage Dependabot alerts:

1. Go to **Security** → **Dependabot**
2. Review and merge dependency update PRs weekly
3. Enable **Dependabot security updates** (should be on by default)

---

## Repository Settings

### General Settings

1. Go to **Settings** → **General**

#### Features to Enable:
- ✅ Issues
- ✅ Projects (if using project boards)
- ✅ Discussions (optional, for community)
- ✅ Preserve this repository (if important)

#### Pull Requests:
- ✅ Allow squash merging (recommended)
- ✅ Allow merge commits
- ❌ Allow rebase merging (can cause issues)
- ✅ Always suggest updating pull request branches
- ✅ Automatically delete head branches

---

## Deployment Configuration

### Railway Integration

If deploying to Railway:

1. Connect your GitHub repository to Railway
2. Railway will automatically deploy on push to `main`
3. The `deploy.yml` workflow will run tests before Railway deploys

### Environment Variables on Railway

Set these in Railway dashboard:

```
DISCORD_TOKEN=your_bot_token_here
```

Railway will automatically use:
- `config/Procfile` for process definition
- `config/nixpacks.toml` for build configuration

---

## Notifications

### GitHub Actions Notifications

To get notified when CI fails:

1. Go to **Settings** → **Notifications**
2. Under "Actions":
   - ✅ Enable notifications for failed workflows
   - Choose: Email or GitHub notifications

### Dependabot Notifications

1. Go to **Settings** → **Notifications**
2. Under "Dependabot alerts":
   - ✅ Enable notifications for new vulnerabilities

---

## Badges for README

Add these badges to your `README.md`:

```markdown
![Tests](https://github.com/abdullah-fr/QuettaTeaBot/workflows/Discord%20Bot%20Tests/badge.svg)
![Deploy](https://github.com/abdullah-fr/QuettaTeaBot/workflows/Deploy%20to%20Production/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)
```

---

## Collaboration Settings

### If Working with a Team:

1. Go to **Settings** → **Collaborators**
2. Add team members with appropriate permissions:
   - **Admin**: Full access
   - **Write**: Can push to branches (not main if protected)
   - **Read**: Can view and clone

### Code Owners (Optional)

Create `.github/CODEOWNERS`:

```
# Default owners for everything
* @abdullah-fr

# Specific owners for different areas
/src/ @abdullah-fr
/tests/ @abdullah-fr
/.github/ @abdullah-fr
```

---

## Issue Templates (Optional)

Create issue templates for better bug reports:

1. Go to **Settings** → **Features** → **Issues** → **Set up templates**
2. Add templates for:
   - Bug reports
   - Feature requests
   - Questions

---

## Security

### Security Policy

Create `SECURITY.md` in your repository root:

```markdown
# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please email:
- Email: your-email@example.com

Please do not open public issues for security vulnerabilities.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
```

### Enable Security Features:

1. Go to **Settings** → **Security & analysis**
2. Enable:
   - ✅ Dependency graph
   - ✅ Dependabot alerts
   - ✅ Dependabot security updates
   - ✅ Secret scanning (if available)

---

## Summary Checklist

After setting up, verify:

- [ ] Branch protection enabled on `main`
- [ ] GitHub Actions permissions configured
- [ ] Dependabot enabled
- [ ] Repository settings optimized
- [ ] Deployment configured (Railway)
- [ ] Notifications enabled
- [ ] Badges added to README
- [ ] Security features enabled

---

## Troubleshooting

### CI Fails on Push

1. Check the Actions tab for error details
2. Run tests locally: `pytest tests/ -v`
3. Ensure all dependencies are in `requirements.txt`

### Branch Protection Blocks Push

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Push to feature branch: `git push origin feature/my-feature`
3. Create a Pull Request on GitHub
4. Merge after tests pass

### Dependabot PRs Failing

1. Review the PR details
2. Check if breaking changes in dependencies
3. Update code if needed
4. Merge or close the PR

---

## Need Help?

- GitHub Actions Docs: https://docs.github.com/en/actions
- Branch Protection: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches
- Dependabot: https://docs.github.com/en/code-security/dependabot

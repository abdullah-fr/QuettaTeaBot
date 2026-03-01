# GitHub Actions Workflows

This directory contains CI/CD workflows for the Discord Bot project.

## Workflows

### 1. `test.yml` - Main Test Pipeline
**Triggers:** Push to main/develop, Pull Requests

**Jobs:**
- **test**: Runs pytest across Python 3.10, 3.11, 3.12
- **lint**: Runs flake8 and black for code quality
- **security**: Checks for security vulnerabilities with safety

**Purpose:** Ensures code quality and test coverage on every commit.

---

### 2. `pr-checks.yml` - Pull Request Validation
**Triggers:** PR opened, synchronized, reopened

**Jobs:**
- **validate**: Syntax checks, test execution, TODO detection
- **test-coverage**: Generates coverage reports

**Purpose:** Validates PRs before merging.

---

### 3. `deploy.yml` - Production Deployment
**Triggers:** Push to main (excluding docs/tests)

**Jobs:**
- **test-before-deploy**: Runs full test suite
- **deploy**: Triggers Railway deployment

**Purpose:** Automated deployment after successful tests.

---

### 4. `scheduled-tests.yml` - Nightly Health Checks
**Triggers:** Daily at 2 AM UTC, Manual dispatch

**Jobs:**
- **nightly-tests**: Full test suite execution
- **health-check**: Verifies critical files exist

**Purpose:** Catches issues early with regular testing.

---

## Configuration Files

### `dependabot.yml`
- Automatically updates Python dependencies weekly
- Updates GitHub Actions versions
- Creates PRs for dependency updates

### `PULL_REQUEST_TEMPLATE.md`
- Standardized PR description format
- Checklist for contributors
- Ensures consistent PR quality

---

## Local Testing

Before pushing, run locally:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific markers
pytest tests/ -m "unit"
pytest tests/ -m "ramadan"

# Check code style
flake8 .
black --check .
```

---

## Badges

Add these to your README.md:

```markdown
![Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Discord%20Bot%20Tests/badge.svg)
![Deploy](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Deploy%20to%20Production/badge.svg)
```

---

## Secrets Required

For full CI/CD functionality, configure these secrets in GitHub:

- `DISCORD_TOKEN` (if needed for integration tests)
- Railway deployment is automatic via GitHub integration

---

## Troubleshooting

**Tests fail in CI but pass locally:**
- Check Python version compatibility
- Verify all dependencies in requirements.txt
- Check for environment-specific issues

**Deployment fails:**
- Verify Railway connection
- Check bot_data.json exists
- Review Railway logs

**Coverage reports missing:**
- Ensure pytest-cov is installed
- Check artifact upload permissions

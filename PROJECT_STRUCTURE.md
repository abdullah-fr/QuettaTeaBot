# Project Structure

This document describes the organization of the Discord Bot project.

## Directory Layout

```
QuettaTeaBot/
├── .github/                    # GitHub configuration
│   ├── workflows/              # CI/CD pipelines
│   │   ├── test.yml           # Main test pipeline
│   │   ├── pr-checks.yml      # PR validation
│   │   ├── deploy.yml         # Production deployment
│   │   ├── scheduled-tests.yml # Nightly tests
│   │   └── README.md          # Workflows documentation
│   ├── dependabot.yml         # Dependency updates
│   └── PULL_REQUEST_TEMPLATE.md
│
├── config/                     # Configuration files
│   └── (deployment configs in root)
│
├── data/                       # Data storage
│   ├── bot_data.json          # Bot persistent data
│   ├── __init__.py
│   └── .gitkeep
│
├── docs/                       # Documentation
│   ├── DEPLOYMENT_READY.md    # Deployment guide
│   ├── RAMADAN_COMMANDS.md    # Ramadan features docs
│   └── .gitkeep
│
├── src/                        # Source code
│   ├── __init__.py
│   ├── main_bot.py            # Main bot entry point
│   ├── ramadan_features.py    # Ramadan features module
│   ├── api_helpers.py         # External API helpers
│   └── question_bank.py       # Question/content bank
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── core/                  # Core testing infrastructure
│   │   ├── __init__.py
│   │   └── base_test.py       # Base test class
│   ├── features/              # Feature tests
│   │   └── __init__.py
│   └── utils/                 # Test utilities
│       └── __init__.py
│
├── .env                        # Environment variables (not in git)
├── .gitignore                  # Git ignore rules
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
├── PROJECT_STRUCTURE.md        # This file
└── README.md                   # Project README

```

## Naming Conventions

### Files
- **Python modules**: `snake_case.py` (e.g., `main_bot.py`, `api_helpers.py`)
- **Configuration**: `PascalCase` or `lowercase` (e.g., `Procfile`, `pytest.ini`)
- **Documentation**: `SCREAMING_SNAKE_CASE.md` (e.g., `README.md`, `DEPLOYMENT_READY.md`)

### Directories
- **Source code**: `src/` - All bot logic
- **Tests**: `tests/` - All test files
- **Data**: `data/` - Persistent storage
- **Config**: `config/` - Deployment configuration
- **Docs**: `docs/` - Documentation files

### Code Style
- **Classes**: `PascalCase` (e.g., `BaseTest`)
- **Functions**: `snake_case` (e.g., `fetch_trivia_question`)
- **Constants**: `SCREAMING_SNAKE_CASE` (e.g., `BOT_DATA_FILE`)
- **Variables**: `snake_case` (e.g., `sticky_message_id`)

## Module Organization

### `src/main_bot.py`
Main bot entry point containing:
- Bot initialization
- Event handlers
- Command definitions
- Feature integrations

### `src/ramadan_features.py`
Ramadan-specific features:
- Prayer times
- Hadith/Ayat commands
- Automated reminders
- Countdown timers

### `src/api_helpers.py`
External API integrations:
- Trivia questions
- Riddles
- Jokes
- Quotes
- Roasts/Compliments

### `src/question_bank.py`
Static content storage:
- Would You Rather questions
- Conversation starters
- Game content

## Data Files

### `data/bot_data.json`
Persistent bot data structure:
```json
{
  "daily_trivia": {...},
  "daily_riddle": {...},
  "streaks": {...},
  "pets": {...},
  "inventory": {...},
  "voice_time": {...}
}
```

## Configuration Files

### `Procfile`
Railway/Heroku process definition:
```
worker: python src/main_bot.py
```

### `nixpacks.toml`
Railway build configuration with Python setup.

### `pytest.ini`
Test configuration with markers and settings.

## Testing Structure

### `tests/core/base_test.py`
Base class providing:
- Test lifecycle management
- Logging utilities
- JSON data helpers
- Custom assertions

### `tests/features/`
Feature-specific test suites (to be added):
- `test_ramadan_features.py`
- `test_trivia_commands.py`
- `test_pet_system.py`
- etc.

### `tests/utils/`
Testing utilities (to be added):
- Mock helpers
- Discord UI simulators
- API mocking utilities

## CI/CD Workflows

### Test Pipeline (`test.yml`)
- Runs on every push/PR
- Tests across Python 3.10, 3.11, 3.12
- Linting and security checks

### PR Checks (`pr-checks.yml`)
- Validates PRs before merge
- Syntax validation
- Coverage reports

### Deployment (`deploy.yml`)
- Runs tests before deploy
- Auto-deploys to Railway on main branch

### Scheduled Tests (`scheduled-tests.yml`)
- Daily health checks at 2 AM UTC
- Dependency update checks

## Development Workflow

1. **Local Development**
   ```bash
   # Install dependencies
   pip install -r requirements.txt

   # Run bot locally
   python src/main_bot.py

   # Run tests
   pytest tests/ -v
   ```

2. **Making Changes**
   - Create feature branch
   - Make changes in appropriate `src/` files
   - Add tests in `tests/features/`
   - Run tests locally
   - Create PR

3. **Deployment**
   - Merge to main branch
   - CI/CD runs tests automatically
   - Auto-deploys to Railway if tests pass

## Best Practices

1. **Code Organization**
   - Keep bot logic in `src/`
   - Keep tests in `tests/`
   - Keep docs in `docs/`
   - Keep config in `config/`

2. **Testing**
   - Write tests for new features
   - Use appropriate test markers
   - Mock external API calls
   - Validate state changes

3. **Documentation**
   - Update docs when adding features
   - Keep README.md current
   - Document complex logic
   - Add docstrings to functions

4. **Version Control**
   - Use meaningful commit messages
   - Follow conventional commits
   - Keep commits focused
   - Review before pushing

## Migration Notes

This structure was reorganized from a flat layout to improve:
- **Maintainability**: Clear separation of concerns
- **Testability**: Isolated test infrastructure
- **Scalability**: Easy to add new features
- **Professionalism**: Industry-standard layout

All imports and paths have been updated to reflect the new structure.

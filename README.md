# 🍵 Quetta Tea Bot

![Tests](https://github.com/abdullah-fr/QuettaTeaBot/workflows/Discord%20Bot%20Tests/badge.svg)
![Deploy](https://github.com/abdullah-fr/QuettaTeaBot/workflows/Deploy%20to%20Production/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)

A comprehensive Discord bot with 25+ features including games, automation, role management, Ramadan features, and more. Built with discord.py and deployed on Railway with full CI/CD pipeline.

---

## 📋 Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Contributing](#-contributing)
- [Documentation](#-documentation)

---

## ✨ Features

### 🎮 Games & Entertainment
- **Daily Trivia** - Tracks answers, reveals after 2 minutes
- **Daily Riddle** - 5-minute timer, first correct answer wins
- **Would You Rather** - Daily questions with reactions
- **Guess The Song** - Pakistani/Indian/English music quiz
- **FirstType Game** - Speed typing competition
- **Pictionary** - Drawing and guessing game
- **Joke Command** - Random jokes on demand

### 🎨 Role Management
- **60 Color Roles** - Interactive button selection
- **Hobby Reaction Roles** - Auto-assign based on reactions
- **Notification Toggle** - Users can opt in/out of notifications
- **Auto-assign Unverified** - New members get unverified role

### 🕌 Ramadan Features
- **Prayer Times** - Sehri & Iftar times for Pakistani cities
- **Automated Reminders** - 15 min before Sehri, at Iftar time
- **Daily Hadith** - Authentic Ramadan hadiths (8 PM PKT)
- **Daily Ayat** - Quranic verses (9 AM PKT)
- **Countdown Timers** - Real-time countdown to Sehri/Iftar
- **Iftar Dua** - Authentic dua posted at Iftar time

### 🎯 Engagement & Automation
- **Daily Streak System** - Track user participation
- **Pet System** - Virtual pets with inventory
- **Voice Time Tracking** - Monitor VC participation
- **QOTD** - Question of the Day
- **Conversation Starters** - Auto-posted prompts
- **Roast/Compliment** - Fun interactive commands

### 🛡️ Moderation & Utility
- **Message Delete Logs** - Track deleted messages
- **Sticky Intro Message** - Auto-repost intro in channel
- **Milestone Celebrations** - Auto-celebrate member milestones
- **Server Stats** - Real-time server statistics

---

## 📁 Project Structure

```
QuettaTeaBot/
├── .github/                    # GitHub configuration
│   ├── workflows/              # CI/CD pipelines
│   │   ├── test.yml           # Main test pipeline (Python 3.10-3.12)
│   │   ├── pr-checks.yml      # PR validation & coverage
│   │   ├── deploy.yml         # Production deployment
│   │   └── scheduled-tests.yml # Nightly health checks
│   ├── dependabot.yml         # Automated dependency updates
│   └── PULL_REQUEST_TEMPLATE.md
│
├── src/                        # Source code
│   ├── __init__.py
│   ├── main_bot.py            # Main bot entry point
│   ├── ramadan_features.py    # Ramadan features module
│   ├── api_helpers.py         # External API integrations
│   └── question_bank.py       # Static content & questions
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_smoke.py          # Smoke tests (11 tests)
│   ├── core/                  # Core testing infrastructure
│   │   ├── __init__.py
│   │   └── base_test.py       # Base test class
│   ├── features/              # Feature-specific tests
│   │   └── __init__.py
│   └── utils/                 # Test utilities & mocks
│       └── __init__.py
│
├── data/                       # Data storage
│   ├── bot_data.json          # Persistent bot data
│   ├── __init__.py
│   └── .gitkeep
│
├── docs/                       # Documentation
│   ├── DEPLOYMENT_READY.md    # Deployment guide
│   ├── RAMADAN_COMMANDS.md    # Ramadan features reference
│   └── GITHUB_SETUP.md        # GitHub configuration guide
│
├── Procfile                    # Railway/Heroku process definition
├── nixpacks.toml               # Railway build configuration
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in git)
├── .gitignore                  # Git ignore rules
├── PROJECT_STRUCTURE.md        # Detailed structure documentation
└── README.md                   # This file
```

### Key Files

- **`src/main_bot.py`** - Main bot logic, event handlers, commands
- **`src/ramadan_features.py`** - Prayer times, hadiths, automated tasks
- **`src/api_helpers.py`** - External API calls (trivia, jokes, etc.)
- **`src/question_bank.py`** - Static content for games
- **`data/bot_data.json`** - Persistent storage for streaks, pets, inventory
- **`tests/core/base_test.py`** - Base test class with utilities
- **`Procfile`** - Defines how Railway runs the bot
- **`nixpacks.toml`** - Railway build configuration

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10, 3.11, or 3.12
- Discord Bot Token ([Get one here](https://discord.com/developers/applications))
- Git

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/abdullah-fr/QuettaTeaBot.git
   cd QuettaTeaBot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Create .env file
   echo "DISCORD_TOKEN=your_bot_token_here" > .env
   ```

4. **Run the bot**
   ```bash
   cd src && python main_bot.py
   ```

5. **Verify it's working**
   - Bot should appear online in Discord
   - Try `!ramadan-times` or `!trivia` commands

---

## 💻 Development

### Setting Up Development Environment

```bash
# Install development dependencies
pip install -r requirements.txt

# Install testing tools
pip install pytest pytest-asyncio pytest-cov flake8 black

# Run tests
pytest tests/ -v

# Check code style
flake8 src/
black --check src/
```

### Project Conventions

#### Code Style
- **Classes**: `PascalCase` (e.g., `BaseTest`)
- **Functions**: `snake_case` (e.g., `fetch_trivia_question`)
- **Constants**: `SCREAMING_SNAKE_CASE` (e.g., `BOT_DATA_FILE`)
- **Variables**: `snake_case` (e.g., `sticky_message_id`)

#### File Naming
- **Python modules**: `snake_case.py`
- **Documentation**: `SCREAMING_SNAKE_CASE.md`
- **Configuration**: `lowercase` or `PascalCase`

#### Git Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/):
```
feat: add new feature
fix: bug fix
test: add or update tests
docs: documentation changes
refactor: code refactoring
ci: CI/CD changes
chore: maintenance tasks
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test markers
pytest tests/ -m "unit"          # Unit tests only
pytest tests/ -m "ramadan"       # Ramadan feature tests
pytest tests/ -m "integration"   # Integration tests

# Run specific test file
pytest tests/test_smoke.py -v
```

### Test Markers

Defined in `pytest.ini`:
- `unit` - Unit tests for individual functions
- `integration` - Integration tests for bot features
- `slow` - Tests that take longer to run
- `ramadan` - Ramadan feature tests
- `api` - Tests involving API calls
- `database` - Tests interacting with bot_data.json
- `commands` - Bot command tests
- `buttons` - Button interaction tests
- `embeds` - Embed validation tests
- `roles` - Role assignment tests

### Current Test Coverage

```
✅ 11 Smoke Tests Passing
- Project structure validation
- Source file existence
- bot_data.json validity
- Configuration file checks
- BaseTest class functionality
```

---

## 🚢 Deployment

### Railway Deployment (Recommended)

1. **Connect Repository**
   - Go to [Railway](https://railway.app)
   - Create new project from GitHub repo
   - Select `QuettaTeaBot` repository

2. **Configure Environment**
   - Add environment variable: `DISCORD_TOKEN=your_token`
   - Railway auto-detects `nixpacks.toml` and `Procfile`

3. **Deploy**
   - Railway automatically deploys on push to `main`
   - Monitor logs in Railway dashboard

### Manual Deployment

```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Run the bot
cd src && python main_bot.py
```

### Environment Variables

Required:
- `DISCORD_TOKEN` - Your Discord bot token

Optional:
- `PYTHONPATH` - Set to project root if needed

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflows

#### 1. **Test Pipeline** (`test.yml`)
- **Triggers**: Push to main/develop, Pull Requests
- **Jobs**:
  - Test across Python 3.10, 3.11, 3.12
  - Lint with flake8 and black
  - Security checks with safety
- **Purpose**: Ensure code quality on every commit

#### 2. **PR Checks** (`pr-checks.yml`)
- **Triggers**: PR opened, synchronized, reopened
- **Jobs**:
  - Syntax validation
  - Full test suite
  - Coverage reports
  - PR size warnings
- **Purpose**: Validate PRs before merging

#### 3. **Deploy** (`deploy.yml`)
- **Triggers**: Push to main (excluding docs/tests)
- **Jobs**:
  - Run tests before deploy
  - Trigger Railway deployment
- **Purpose**: Automated production deployment

#### 4. **Scheduled Tests** (`scheduled-tests.yml`)
- **Triggers**: Daily at 2 AM UTC, Manual dispatch
- **Jobs**:
  - Nightly test suite
  - Dependency update checks
  - Health checks
- **Purpose**: Catch issues early

### Dependabot

- Automatically updates dependencies weekly
- Creates PRs for Python packages and GitHub Actions
- Configured in `.github/dependabot.yml`

---

## 🤝 Contributing

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code in `src/`
   - Add tests in `tests/features/`
   - Update documentation

3. **Run tests locally**
   ```bash
   pytest tests/ -v
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   - Go to GitHub and create Pull Request
   - Fill out the PR template
   - Wait for CI checks to pass

6. **Merge after approval**
   - Squash and merge recommended
   - Delete branch after merge

### Pull Request Guidelines

- Use the PR template (`.github/PULL_REQUEST_TEMPLATE.md`)
- Ensure all tests pass
- Add tests for new features
- Update documentation
- Follow code style conventions
- Keep PRs focused and small

---

## 📚 Documentation

### Available Documentation

- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Detailed project structure
- **[docs/DEPLOYMENT_READY.md](docs/DEPLOYMENT_READY.md)** - Deployment guide
- **[docs/RAMADAN_COMMANDS.md](docs/RAMADAN_COMMANDS.md)** - Ramadan features reference
- **[docs/GITHUB_SETUP.md](docs/GITHUB_SETUP.md)** - GitHub configuration guide
- **[.github/workflows/README.md](.github/workflows/README.md)** - CI/CD workflows

### Command Reference

#### Ramadan Commands
```
!ramadan-times              - Show Sehri & Iftar times
!ramadan-city [city]        - Change city for prayer times
!hadith                     - Random Ramadan hadith
!ayat                       - Random Quranic verse
!iftar-countdown            - Countdown to Iftar
!sehri-countdown            - Countdown to Sehri closing
```

#### Game Commands
```
!trivia                     - Start daily trivia
!riddle                     - Start daily riddle
!wyr                        - Would You Rather
!guess-song                 - Guess the song game
!joke                       - Random joke
```

#### Utility Commands
```
!qotd                       - Question of the Day
!roast [@user]              - Roast a user (friendly)
!compliment [@user]         - Compliment a user
!conversation-starter       - Get a conversation prompt
```

---

## 🔧 Troubleshooting

### Common Issues

**Bot not responding to commands:**
- Check bot has proper permissions in Discord
- Verify `DISCORD_TOKEN` is correct
- Check bot is online in Discord

**Import errors:**
- Ensure you're running from project root
- Check all dependencies are installed: `pip install -r requirements.txt`

**Tests failing:**
- Run `pytest tests/ -v` to see detailed errors
- Check Python version (3.10, 3.11, or 3.12)
- Verify `data/bot_data.json` exists

**Railway deployment fails:**
- Check Railway logs for errors
- Verify `DISCORD_TOKEN` environment variable is set
- Ensure `Procfile` and `nixpacks.toml` are in root

---

## 📊 Project Stats

- **Lines of Code**: ~3000+
- **Features**: 25+
- **Test Coverage**: Growing (11 smoke tests currently)
- **Python Versions**: 3.10, 3.11, 3.12
- **CI/CD**: Fully automated with GitHub Actions
- **Deployment**: Railway (auto-deploy on push)

---

## 📝 License

This project is private and maintained by [@abdullah-fr](https://github.com/abdullah-fr).

---

## 🙏 Acknowledgments

- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Deployed on [Railway](https://railway.app)
- CI/CD powered by [GitHub Actions](https://github.com/features/actions)
- Testing with [pytest](https://pytest.org)

---

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation in `docs/`
- Review CI/CD logs for deployment issues

---

**Last Updated**: March 1, 2026
**Version**: 1.0.0
**Status**: ✅ Production Ready

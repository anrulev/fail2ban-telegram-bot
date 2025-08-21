# Changelog

[![Язык-Русский](https://img.shields.io/badge/%D0%AF%D0%B7%D1%8B%D0%BA-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-green?logo=google-translate&style=flat)](CHANGELOG.md) ![Language-English](https://img.shields.io/badge/Language-English-lightgrey?logo=google-translate&style=flat)

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Support for automatic hostname detection via `socket.gethostname()`
- Optional `HOSTNAME` environment variable for custom server names
- Hostname display in Telegram notifications and `/latest` command
- Maintainer documentation in `docs/maintainers/`
- Helper scripts in `scripts/maintainers/`

### Changed
- Updated repository URL to `anrulev/fail2ban-telegram-bot`
- Removed Docker Hub publishing sections from public README
- Moved internal documentation to maintainer sections
- Improved documentation with optional HOSTNAME variable

### Fixed
- English README restoration after partial content loss
- Documentation consistency across all files

## [1.0.0] - 2025-01-15

### Added
- Initial release of Fail2Ban Telegram Bot
- Real-time monitoring of Fail2Ban log files
- Telegram notifications for new IP bans
- Docker container support
- Docker Compose configuration
- Bot commands: `/start`, `/help`, `/latest`
- Optional status commands: `/status`, `/jails` (requires fail2ban-client)
- Environment-based configuration
- Log rotation support
- Resource limits in Docker Compose
- Helper script `run.sh` for easy setup
- Health check script `check_bot.sh`
- Support for multiple Fail2Ban log formats
- Error handling and logging
- Non-privileged container execution

### Features
- 🔍 Real-time log monitoring
- 🚨 Instant Telegram notifications
- 📊 Status checking commands
- 🔒 Jail information display
- 🐳 Docker containerization
- 🧱 Optional fail2ban-client integration

### Technical Details
- Python 3.12 base image
- Telebot library for Telegram integration
- Configurable check intervals
- Maximum alerts per run limit
- Automatic log position tracking
- Graceful error handling
- Threaded monitoring and bot operation

---

## Version History

- **1.0.0** - Initial stable release with core functionality
- **Unreleased** - Added hostname support and maintainer tools

## Contributing

When contributing to this project, please update this changelog with your changes under the appropriate version section.

## Release Process

1. Update version in files:
   - `version.py` - `__version__` variable
   - `Dockerfile` - image tag (if used)
   - `README.md` - version mentions (if any)
2. Add new section to CHANGELOG.md
3. Create git tag for the version: `git tag v1.0.0`
4. Update release notes on GitHub

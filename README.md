<div align=center>

<img src="./Assets/akari-v2.1-heart.png" alt="Akari" width=200 height=200/>

# Akari

[![Required Python Version](https://img.shields.io/badge/Python-3.8%20|%203.9%20|%203.10%20|%203.11-blue?logo=python&logoColor=white)](https://github.com/No767/Akari/blob/dev/pyproject.toml) [![CodeQL](https://github.com/No767/Akari/actions/workflows/codeql.yml/badge.svg)](https://github.com/No767/Akari/actions/workflows/codeql.yml) [![Docker Build](https://github.com/No767/Akari/actions/workflows/docker-build.yml/badge.svg)](https://github.com/No767/Akari/actions/workflows/docker-build.yml) [![Lint](https://github.com/No767/Akari/actions/workflows/lint.yml/badge.svg)](https://github.com/No767/Akari/actions/workflows/lint.yml) [![Tests](https://github.com/No767/Akari/actions/workflows/tests.yml/badge.svg)](https://github.com/No767/Akari/actions/workflows/tests.yml) [![codecov](https://codecov.io/gh/No767/Akari/branch/dev/graph/badge.svg?token=n6wqqdNDLr)](https://codecov.io/gh/No767/Akari) [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/No767/Akari/dev.svg)](https://results.pre-commit.ci/latest/github/No767/Akari/dev) ![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/No767/Akari?label=Release&logo=github&sort=semver) ![GitHub](https://img.shields.io/github/license/No767/Akari?label=License&logo=github)

A Discord bot focused on providing modern utility to the modern-day support server

<div align=left>

## Akari

Akari is a utility toolkit bot for Discord servers. Akari contains a variety of commands, ranging from tags, to moderation. Akari is designed to be used internally for Kumiko's Support Server, but can be also used by others as well.


# Features

- [x] Custom tags
- [ ] Role management system
- [ ] Utility Commands
- [ ] Modmail

# Prefix

Just like with Kumiko, Akari uses `/` as the prefix

# Inviting the Bot

Akari is still in development, and not ready for public use.

# Resources

- [GHCR](https://github.com/No767/Akari/pkgs/container/akari)
- [Docker Hub](https://hub.docker.com/r/no767/akari)

# Setup Notes

Don't forget to include the pg_trgm module

```sql
CREATE EXTENSION pg_trgm;
```

# Licensing

Apache-2.0

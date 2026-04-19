# ExpenseOverseer

A Telegram bot for quickly and easily logging personal expenses and income, with built-in analytics, multi-currency support, and multi-language UI.

Built with [aiogram](https://docs.aiogram.dev/) (async Telegram Bot API framework), [SQLAlchemy](https://www.sqlalchemy.org/) (async with `asyncpg`), [Alembic](https://alembic.sqlalchemy.org/) for migrations, and [Dynaconf](https://www.dynaconf.com/) for configuration. Packaging and dependency management is handled by [uv](https://docs.astral.sh/uv/).

## Features

- **Fast transaction logging** — record expenses or income with amount, currency, category, and description directly from Telegram.
- **Edit & delete** — review and update recent transactions via inline keyboards (`/modify`).
- **Analytics** (`/analytics`):
  - Pie chart by category
  - Cumulative spending chart
  - CSV export of raw transaction data
- **Multi-currency** — `BYN`, `USD`, `RUB`, `EUR`, `CNY`, `BTC`, `ETH` (default: `BYN`).
- **Multi-language UI** — English, Russian, and Belarusian; translations live in [`core/language/texts.json`](core/language/texts.json).
- **User whitelist** — access is gated by Telegram username via the `users_whitelist` table.
- **Structured logging** — JSON logs via `python-json-logger`.
- **Dockerized** — production image based on `ghcr.io/astral-sh/uv:python3.14-alpine`.

## Bot commands

| Command      | Description                                  |
|--------------|----------------------------------------------|
| `/modify`    | Show recent transactions and edit/delete them |
| `/analytics` | Open the transaction analytics tools          |
| `/settings`  | Configure bot settings                        |
| `/help`      | Show help                                     |

To log a transaction, just send a message with the amount and an optional description; the parser routes it through the transaction router.

## Project layout

```
.
├── main.py                  # Entry point — builds Dispatcher, registers routers & middlewares
├── core/
│   ├── analytics/           # Charts (matplotlib) and CSV export
│   ├── keyboards/           # Inline keyboards (categories, analytics, edit)
│   ├── language/            # i18n texts + loader
│   ├── middlewares/         # DB session, user translation, logging middlewares
│   └── routers/             # aiogram routers: transactions, analytics, settings, general
├── models/
│   ├── db_models/           # SQLAlchemy models (users, transactions, categories, whitelist)
│   ├── dto/                 # Pydantic DTOs
│   └── enums/               # Currency, language, transaction type, flow type
├── utils/                   # Config, DB engine, FSM helpers, init commands
├── alembic/                 # DB migrations
├── tests/
├── settings.toml            # Dynaconf defaults
├── pyproject.toml           # uv + ruff + project metadata
├── Dockerfile
├── Makefile                 # Common dev tasks
└── build.sh                 # Docker build helper with git metadata tagging
```

## Requirements

- Python **>=3.13, <3.14**
- PostgreSQL (reachable via `asyncpg`)
- [uv](https://docs.astral.sh/uv/) for dependency management
- A Telegram bot token (see [@BotFather](https://t.me/BotFather))

## Configuration

Settings are loaded by Dynaconf from [`settings.toml`](settings.toml) and an optional `.secrets.toml`. Environment variables prefixed with `DYNACONF_` also override values.

Defaults (`[default]` section of `settings.toml`):

| Key                      | Default             | Purpose                                    |
|--------------------------|---------------------|--------------------------------------------|
| `APPNAME`                | `Expense Overseer`  | Application name                           |
| `VERSION`                | `0.6.0`             | App version shown on startup               |
| `DATABASE_HOST`          | `localhost`         | PostgreSQL host                            |
| `DATABASE_PORT`          | `5432`              | PostgreSQL port                            |
| `DATABASE_USER`          | `postgres`          | PostgreSQL user                            |
| `DATABASE_PASSWORD`      | `postgres`          | PostgreSQL password                        |
| `DATABASE_DB`            | `expense_overseer`  | PostgreSQL database name                   |
| `DATABASE_ECHO_MODE`     | `false`             | Echo SQL statements                        |
| `TG_BOT_TOKEN`           | *(empty)*           | **Required** — Telegram bot token          |
| `LAST_TRANSACTIONS_QTY`  | `10`                | How many recent transactions `/modify` shows |
| `MISSING_TEXT_PLACEHOLDER` | `This text has not been translated, sorry :(` | Fallback when a translation is missing |

Create a `.secrets.toml` (git-ignored) to store the bot token:

```toml
[default]
TG_BOT_TOKEN = "123456:ABC-your-telegram-bot-token"
```

## Local development

```bash
# 1. Install dependencies (creates a venv via uv)
make install

# 2. Start PostgreSQL (any method; example with Docker)
docker run --name expense-db -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_DB=expense_overseer -p 5432:5432 -d postgres:16

# 3. Apply migrations
uv run alembic upgrade head

# 4. Run the bot
make run
# or: uv run main.py
```

### Make targets

| Target                   | Description                                |
|--------------------------|--------------------------------------------|
| `make install`           | Install dependencies (including dev extras) |
| `make run`               | Run the bot locally                        |
| `make migrate`           | Apply Alembic migrations                   |
| `make format`            | Run `ruff format` and autofix lint issues  |
| `make lint`              | Run `ruff check` and `ruff format --check` |
| `make test`              | Run the test suite with `pytest`           |
| `make clean`             | Remove caches and compiled artifacts       |
| `make lock-upgrade`      | Upgrade `uv.lock`                          |
| `make build-docker`      | Build the container image                  |
| `make run-docker`        | Run the bot via `docker-compose`           |

### Granting access to users

The bot checks incoming usernames against the `users_whitelist` table. Add an entry for each allowed Telegram username (without the leading `@`) before users can interact with the bot.

## Docker

Build and run via the helper script, which pulls the latest commit, tags the image with a timestamp + git hash, and runs `docker build`:

```bash
./build.sh
```

Or use the provided `Dockerfile` directly:

```bash
docker build -t expense-overseer:latest .
docker run --rm \
    -e DYNACONF_TG_BOT_TOKEN="$TG_BOT_TOKEN" \
    -e DYNACONF_DATABASE_HOST=host.docker.internal \
    expense-overseer:latest
```

The container runs `alembic upgrade head` and then starts `main.py`.

## Testing

```bash
make test
```

Tests are configured through `pyproject.toml` (pytest + pytest-asyncio) and run with `ENV_FOR_DYNACONF=test`, which switches to the `[test]` settings block (e.g. `DATABASE_HOST = "postgres"`).

## Tech stack

- **Runtime:** Python 3.13
- **Bot framework:** aiogram 3.x (HTML parse mode, FSM, middlewares)
- **Database:** PostgreSQL via SQLAlchemy 2.x async + asyncpg; migrations with Alembic
- **Charts:** matplotlib (Plotly available in dev extras)
- **Config:** Dynaconf
- **Tooling:** uv, ruff, black, pytest, pytest-asyncio, coverage, freezegun

## License

Released under the terms of the [MIT License](LICENSE).

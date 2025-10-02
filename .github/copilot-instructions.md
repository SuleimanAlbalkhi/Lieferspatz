# Copilot Instructions for Lieferspatz

## Project Overview
- Lieferspatz is a web application using Flask and SQLite for managing restaurant accounts and orders.
- The main database file is `mydatabase.db`.
- User credentials for test accounts are listed in the `README.md`.

## Setup & Developer Workflow
- Required tools: VS Code, Git, SQLite, Flask (install via `pip install flask`), DB Browser for SQLite.
- To start the web application, use the Flask development server (typically `flask run` or a custom script if present).
- Database changes are made directly to `mydatabase.db` using DB Browser for SQLite or via Flask endpoints.

## Key Patterns & Conventions
- All persistent data is stored in `mydatabase.db` (SQLite format).
- User authentication uses hardcoded credentials for demo/testing (see `README.md`).
- No explicit test or build scripts found; manual testing via web interface and DB Browser is expected.
- No custom agent or AI rules files detected; follow standard Flask and SQLite usage patterns.

## Integration Points
- External dependencies: Flask (Python web framework), SQLite (database), DB Browser for SQLite (GUI tool).
- No evidence of microservices or external APIs; all logic is likely contained in a single Flask app.

## Actionable Guidance for AI Agents
- When adding features, ensure changes are compatible with Flask and SQLite.
- Reference `README.md` for test credentials and setup steps.
- If implementing authentication, use the patterns shown in the credentials list.
- Document any new developer workflows or conventions in this file for future agents.

## Example: Adding a New Restaurant
- Update `mydatabase.db` with new credentials using DB Browser or a Flask endpoint.
- Add the new credentials to the list in `README.md` for easy reference.

---
_Last updated: October 2, 2025_

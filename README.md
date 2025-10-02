# Lieferspatz 🚚

A web application for managing restaurant accounts and delivery orders using Flask and SQLite.

## Description

Lieferspatz is a restaurant management system that allows restaurants to handle their accounts and manage delivery orders. Built with Flask and SQLite, it provides a simple and efficient way to manage restaurant operations.

## Prerequisites

Before you begin, ensure you have the following tools installed:

- [VS Code](https://code.visualstudio.com/download) - Code editor
- [Git](https://www.git-scm.com/downloads) - Version control
- [SQLite](https://www.sqlite.org/index.html) - Database
- [DB Browser for SQLite](https://sqlitebrowser.org/) - Database management tool
- Python 3.x

## Setup

1. Clone the repository:
   ```bash
   git clone [repository-url]
   ```

2. Navigate to the project directory:
   ```bash
   cd Lieferspatz
   ```

3. Create and activate a virtual environment:
   ```bash
   # Create virtual environment
   python -m venv .venv

   # Activate virtual environment
   # For Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   # For Windows Command Prompt:
   .\.venv\Scripts\activate.bat
   ```

4. Install Flask:
   ```bash
   python -m pip install flask
   ```

5. Set the Flask application:
   ```bash
   # For Windows PowerShell:
   $env:FLASK_APP = "app.py"
   # For Windows Command Prompt:
   set FLASK_APP=app.py
   ```

6. Start the application:
   ```bash
   python -m flask run
   ```

The application will be available at `http://localhost:5000`

Note: If you get "python command not found", make sure Python is installed and added to your system's PATH.

## Database

The application uses SQLite for data storage. The main database file is `mydatabase.db`. You can view and modify the database using DB Browser for SQLite.

## Test Accounts

The following test accounts are available for development and testing:

| ID | Username  | Password    |
|----|-----------|-------------|
| 1  | KFC      | asd123      |
| 3  | Subway   | qwe789      |
| 4  | McDonald | yxc456      |
| 6  | Damila   | da12345678  |
| 8  | alzaem   | 123         |
| 9  | maki     | 123         |
| 10 | Vapiano  | 123         |

## Contributing

When contributing to this project:
1. Use DB Browser for SQLite for database modifications
2. Follow the existing code structure
3. Test your changes with the provided test accounts
4. Document any new features or changes

## License
© 2025 Lieferspatz
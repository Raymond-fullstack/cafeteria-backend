# Setup and configuration guide

This guide explains how to configure and run the Cafeteria backend from a fresh environment.

## A. Prerequisites

Install the following software independently before running the project:

- Python 3.11 or newer
- MySQL Community Server 8.0 or newer
- MySQL Workbench or another MySQL client (optional but recommended)
- Git (optional for obtaining the source code)

Verify the installed versions:

```bash
python --version
mysql --version
```

If you are on Windows PowerShell, use the same commands in a new terminal window.

## B. Project setup

Obtain the project files and open the project root:

```bash
cd path/to/cafeteria-backend
```

Create a virtual environment:

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Upgrade pip and install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## C. MySQL configuration

Start the local MySQL server using your installed MySQL service manager or via the command line if configured.

Access the MySQL shell:

```bash
mysql -u root -p
```

Create the application database:

```sql
CREATE DATABASE cafeteria_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Create a dedicated user:

```sql
CREATE USER 'cafeteria_user'@'localhost' IDENTIFIED BY 'StrongPassword123';
```

Grant privileges to that database:

```sql
GRANT ALL PRIVILEGES ON cafeteria_db.* TO 'cafeteria_user'@'localhost';
FLUSH PRIVILEGES;
```

Verify connectivity:

```bash
mysql -u cafeteria_user -p cafeteria_db
```

Use your own values for database name, username and password; do not hardcode production credentials into source files.

## D. Environment variables and connection string

Copy the example environment file and customize it:

```bash
cp .env.example .env
```

Modify `.env` with the values for your local MySQL instance. The example file contains variables such as:

```env
DATABASE_URL=mysql+pymysql://cafeteria_user:StrongPassword123@localhost:3306/cafeteria_db?charset=utf8mb4
SECRET_KEY=change-me-to-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ENVIRONMENT=development
BUSINESS_TIMEZONE=Africa/Lagos
APP_NAME=Cafeteria Backend
```

Explanation:

- `mysql+pymysql://` tells SQLAlchemy to use the PyMySQL driver.
- `cafeteria_user` is the MySQL username.
- `StrongPassword123` is the password for the user.
- `localhost` is the database host.
- `3306` is the MySQL port.
- `cafeteria_db` is the database name.
- `charset=utf8mb4` keeps the database using UTF-8 with full Unicode support.

If the username or password includes special characters, URL-encode them before placing them in the connection string.

The application reads these values through the central settings module in `app/config.py` rather than directly from environment variables in many parts of the code.

Ensure `.env` is ignored by Git by keeping `.gitignore` in place.

## E. Database initialization and migrations

Create or update the database structure using Alembic migrations:

```bash
alembic upgrade head
```

When models change, generate a migration:

```bash
alembic revision --autogenerate -m "description of changes"
```

Review the generated migration before applying it. Do not rely on `Base.metadata.create_all()` as a replacement for Alembic.

## F. Initial administrator creation

Create the initial system administrator securely using the bootstrap script:

```bash
python scripts/create_initial_admin.py --username admin --email semakularaymond19@gmail.com --full-name "Semakula Raymond"
```

The script prompts for a password interactively if you do not pass it on the command line. This keeps the root admin credential out of source control and avoids hardcoded production credentials.

To change credentials later, log in with the admin account and update the user data through the relevant user management endpoints or create a new admin user via the API.

## G. Starting the application

Start the FastAPI app in development mode:

```bash
uvicorn app.main:app --reload
```

Expected local URL:

- http://127.0.0.1:8000

Open:

- http://127.0.0.1:8000/docs for Swagger UI
- http://127.0.0.1:8000/redoc for ReDoc
- http://127.0.0.1:8000/health for health check responses

## H. Running tests

Execute the automated tests with:

```bash
pytest
```

The included tests are lightweight app smoke tests. If your project later includes database integration tests, they will require a reachable MySQL instance and the corresponding `.env` file.

## I. Common configuration problems

- Python not recognized: install Python and reopen the terminal.
- Virtual environment activation failures: ensure PowerShell execution policy allows scripts or use `python -m venv .venv` and activate with the required shell-specific command.
- Dependency installation errors: upgrade pip and ensure you are in the project folder and inside the active virtual environment.
- MySQL service not running: start the MySQL service from the system service manager or the MySQL command line utility.
- Incorrect database credentials: verify the username, password and granted privileges.
- Incorrect connection strings: ensure the driver and host values match your database installation.
- Database access denied: verify that the MySQL user has been granted permissions on the application database.
- Missing environment variables: check `.env` and confirm the file is named exactly `.env`.
- Alembic migration errors: inspect the generated SQL, verify the database is reachable, and ensure the migration environment has the proper URL.
- Port conflicts: stop any process already using port 8000 or start the app on another port.
- JWT secret configuration problems: ensure `SECRET_KEY` is set and not left as the placeholder value.

## J. Production configuration notes

Before deploying to a conventional hosting environment:

- Use production database credentials, not local development credentials.
- Set production values for `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`, `ENVIRONMENT` and `BUSINESS_TIMEZONE`.
- Enable HTTPS at the hosting layer or through a reverse proxy.
- Restrict `CORS_ORIGINS` to known trusted frontend origins.
- Use a strong, randomly generated JWT secret.
- Run `alembic upgrade head` as part of deployment.
- Use a process manager such as Supervisor or systemd for long-running app instances.
- Implement regular database backups and restoration procedures.

Do not use Docker or Docker Compose for this project.

# Cafeteria Backend

A FastAPI-based backend for cafeteria operations with user authentication, product catalog management, order processing, wallet and debt tracking, and downloadable financial reports.

## Tech stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- MySQL
- Alembic
- JWT-based authentication
- Excel and PDF exports

## Core features

- Role-based authentication and authorization
- Product management
- Order creation and tracking
- Wallet top-ups and debits
- Debt creation and settlement
- Dashboard reporting
- Excel and PDF export endpoints

## Quick start

1. Review [SETUP.md](./SETUP.md) for full local setup instructions.
2. Create a virtual environment and install dependencies.
3. Configure `.env` from `.env.example`.
4. Run database migrations.
5. Start the app with uvicorn.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .\.venv\Scripts\Activate.ps1 on Windows PowerShell
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

## Documentation

- Setup: [SETUP.md](./SETUP.md)
- API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Notes

The developer is responsible for installing and configuring MySQL and creating their own local database credentials. The application uses environment variables and does not hardcode production secrets.

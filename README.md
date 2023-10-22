
# Montenegro IBAN Validation API

This is a FastAPI-based API for validating International Bank Account Numbers (IBANs) specifically for Montenegro.

## Features
- Validate Montenegro IBAN via a POST endpoint.
- Real-time IBAN validation.
- Store and retrieve IBAN validation history in a PostgreSQL database.
- Suggest likely correct IBAN for incorrect entries.
- Well-documented and user-friendly API.

## Technologies Used
- FastAPI
- PostgreSQL
- SQLAlchemy
- Marshmallow
- Alembic (Placeholder for migrations)

## Requirements
- Python 3.6+
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- Marshmallow
- Alembic (for database migrations)
- PostgreSQL

## Installation
1. Clone this repository.
2. Navigate to the project directory.
3. Install the required packages using pip.
   ```bash
   pip install -r requirements.txt
   ```
4. Setup the PostgreSQL database and update the `DATABASE_URL` in `main.py`.
5. Run Alembic migrations to create the database schema. (Placeholder present, please setup Alembic)

## Running the Application
1. Navigate to the project directory.
2. Run the application using uvicorn.
   ```bash
   uvicorn main:app --reload
   ```

## Usage
Various endpoints are available for different functionalities. Please refer to the FastAPI documentation generated at `http://127.0.0.1:8000/docs`.

## Running Tests
Run the tests using pytest.
```bash
pytest test_main.py
```

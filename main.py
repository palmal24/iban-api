from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
import datetime
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import Depends
from fastapi import FastAPI, HTTPException, Depends
from marshmallow import Schema, fields


# Initialize the FastAPI application
# Function to validate Montenegro IBAN
# Montenegro IBAN has 22 characters and starts with "ME"
# Reorder and replace characters for checksum validation
# Convert letters to numbers for checksum calculation
# Validate checksum
# In-memory storage for validation history
# Placeholder logic for demonstration (replace 'a' with '4', 'b' with '5', etc.)
# Database setup
# ValidationHistory model
# Dependency to get the database session
# Marshmallow Schema for ValidationHistory
# Updated Endpoint with Marshmallow serialization


DATABASE_URL = "postgresql://user:password@localhost/db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(title="Montenegro IBAN Validator",
              description="A simple API to validate Montenegro IBANs")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class IBANModel(BaseModel):
    iban: str


def validate_montenegro_iban(iban: str) -> bool:
    """Validate Montenegro IBAN based on its structure and checksum."""
    if len(iban) != 22 or not iban.startswith('ME'):
        return False
    iban_temp = iban[4:] + '252900' + iban[2:4]
    iban_temp = re.sub(
        r'[A-Z]', lambda x: str(ord(x.group(0)) - ord('A') + 10), iban_temp)
    return int(iban_temp) % 97 == 1


@app.post("/validate_iban/", response_model=IBANModel, summary="Validate Montenegro IBAN")
async def validate_iban_endpoint(iban: IBANModel):
    """Endpoint to validate Montenegro IBAN.
    Takes a JSON object with the IBAN and returns its validity.
    Args:
        iban (IBANModel): IBAN to be validated.
    Returns:
        dict: JSON object with the IBAN and its validity.
    """
    is_valid = validate_montenegro_iban(iban.iban)
    return {"iban": iban.iban, "valid": is_valid}


@app.post("/realtime_validate_iban/", summary="Real-time Validation of Montenegro IBAN")
async def realtime_validate_iban_endpoint(iban: IBANModel):
    """Endpoint for real-time validation of Montenegro IBAN.
    Takes a JSON object with the partial IBAN and returns its validation status so far.
    Args:
        iban (IBANModel): Partial IBAN to be validated.
    Returns:
        dict: JSON object with the IBAN and its partial validation status.
    """
    is_valid_so_far = validate_montenegro_iban(
        iban.iban) if len(iban.iban) == 22 else None
    return {"iban": iban.iban, "valid_so_far": is_valid_so_far}


@app.post("/store_validate_iban/", summary="Store and Validate Montenegro IBAN")
async def store_and_validate_iban_endpoint(iban: IBANModel):
    """Endpoint to store and validate Montenegro IBAN.
    Takes a JSON object with the IBAN, validates it, and stores it along with the validation result and timestamp.
    Args:
        iban (IBANModel): IBAN to be stored and validated.
    Returns:
        dict: JSON object with the IBAN, its validity, and the timestamp.
    """
    is_valid = validate_montenegro_iban(iban.iban)
    timestamp = str(datetime.datetime.now())
    validation_entry = {"iban": iban.iban,
                        "valid": is_valid, "timestamp": timestamp}
    validation_history.append(validation_entry)
    return validation_entry


@app.get("/get_validation_history/", summary="Get Validation History")
async def get_validation_history():
    """Endpoint to retrieve the history of validated IBANs.
    Returns:
        list: List of JSON objects containing IBANs, their validation status, and timestamps.
    """
    return validation_history


def suggest_correct_iban(iban: str) -> str:
    """Suggest the most likely correct Montenegro IBAN.
    This function currently suggests an IBAN by attempting to correct common typos.
    Note: This is a basic version and can be extended for more advanced suggestions.
    Args:
        iban (str): Incorrect IBAN for which a suggestion is needed.
    Returns:
        str: Suggested IBAN.
    """
    suggested_iban = iban.replace('a', '4').replace('b', '5').replace('c', '6')
    return suggested_iban.upper()


@app.post("/suggest_validate_iban/", summary="Suggest and Validate Montenegro IBAN")
async def suggest_and_validate_iban_endpoint(iban: IBANModel):
    """Endpoint to suggest and validate Montenegro IBAN.
    Takes a JSON object with the IBAN, validates it, and if invalid, suggests a likely correct IBAN.
    Args:
        iban (IBANModel): IBAN to be suggested and validated.
    Returns:
        dict: JSON object with the IBAN, its validity, and the suggested IBAN if applicable.
    """
    is_valid = validate_montenegro_iban(iban.iban)
    suggested_iban = suggest_correct_iban(iban.iban) if not is_valid else None
    return {"iban": iban.iban, "valid": is_valid, "suggested_iban": suggested_iban}


class ValidationHistory(Base):
    __tablename__ = 'validation_history'
    id = Column(Integer, primary_key=True, index=True)
    iban = Column(String, index=True)
    valid = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


@app.post("/db_store_validate_iban/", summary="DB Store and Validate Montenegro IBAN")
async def db_store_and_validate_iban_endpoint(iban: IBANModel, db: Session = Depends(get_db)):
    is_valid = validate_montenegro_iban(iban.iban)
    timestamp = datetime.datetime.now()
    db_iban = ValidationHistory(
        iban=iban.iban, valid=is_valid, timestamp=timestamp)
    db.add(db_iban)
    db.commit()
    db.refresh(db_iban)
    return {"iban": db_iban.iban, "valid": db_iban.valid, "timestamp": db_iban.timestamp}


@app.get("/db_get_validation_history/", summary="DB Get Validation History")
async def db_get_validation_history(db: Session = Depends(get_db)):
    return db.query(ValidationHistory).all()


class ValidationHistorySchema(Schema):
    id = fields.Int(dump_only=True)
    iban = fields.Str()
    valid = fields.Bool()
    timestamp = fields.DateTime()


validation_history_schema = ValidationHistorySchema()
validation_histories_schema = ValidationHistorySchema(many=True)


@app.post("/advanced_db_store_validate_iban/", summary="Advanced DB Store and Validate Montenegro IBAN")
async def advanced_db_store_and_validate_iban_endpoint(iban: IBANModel, db: Session = Depends(get_db)):
    is_valid = validate_montenegro_iban(iban.iban)
    timestamp = datetime.datetime.now()
    db_iban = ValidationHistory(
        iban=iban.iban, valid=is_valid, timestamp=timestamp)
    db.add(db_iban)
    db.commit()
    db.refresh(db_iban)
    return validation_history_schema.dump(db_iban)


@app.get("/advanced_db_get_validation_history/", summary="Advanced DB Get Validation History")
async def advanced_db_get_validation_history(db: Session = Depends(get_db)):
    db_data = db.query(ValidationHistory).all()
    return validation_histories_schema.dump(db_data)

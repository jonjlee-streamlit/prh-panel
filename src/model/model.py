from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional
from datetime import date


class Meta(SQLModel, table=True):
    __tablename__ = "meta"
    id: Optional[int] = Field(default=None, primary_key=True)
    modified: date


class Patient(SQLModel, table=True):
    __tablename__ = "patients"

    prw_id: Optional[int] = Field(default=None, primary_key=True)
    mrn: int = Field(unique=True)
    name: str
    sex: str = Field(regex="^[MF]$")
    dob: date
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    pcp: Optional[str] = None

    encounters: List["Encounter"] = Relationship(back_populates="patient")


class Encounter(SQLModel, table=True):
    __tablename__ = "encounters"

    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patient.prw_id")
    encounter_date: date
    type: str
    location: str
    service_provider: Optional[str] = None
    billing_provider: Optional[str] = None
    with_pcp: Optional[bool] = None
    diagnoses: Optional[dict] = None
    level_of_service: Optional[str] = None

    patient: Optional[Patient] = Relationship(back_populates="encounters")

from sqlalchemy.orm import registry
from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional
from datetime import datetime, date, time


class PrwModel(SQLModel, registry=registry()):
    pass


class PrwMeta(PrwModel, table=True):
    __tablename__ = "prw_meta"
    id: Optional[int] = Field(default=None, primary_key=True)
    modified: datetime


class PrwSourcesMeta(PrwModel, table=True):
    __tablename__ = "prw_sources_meta"
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(unique=True)
    modified: datetime


class PrwPatient(PrwModel, table=True):
    __tablename__ = "prw_patients"

    prw_id: Optional[int] = Field(default=None, primary_key=True)
    mrn: int = Field(unique=True)
    name: Optional[str] = None
    sex: str = Field(regex="^[MFO]$")
    dob: date
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    pcp: Optional[str] = None

    encounters: List["PrwEncounter"] = Relationship(back_populates="patient")


class PrwEncounter(PrwModel, table=True):
    __tablename__ = "prw_encounters"

    id: Optional[int] = Field(default=None, primary_key=True)
    mrn: int = Field(foreign_key="prw_patients.mrn")
    location: str
    dept: str
    encounter_date: date
    encounter_time: time
    encounter_type: str
    service_provider: Optional[str] = None
    billing_provider: Optional[str] = None
    with_pcp: Optional[bool] = None
    appt_status: Optional[str] = None
    diagnoses: Optional[str] = None
    level_of_service: Optional[str] = None

    patient: Optional[PrwPatient] = Relationship(back_populates="encounters")

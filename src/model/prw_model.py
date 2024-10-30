from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional
from datetime import datetime, date, time


class Meta(SQLModel, table=True):
    __tablename__ = "meta"
    id: Optional[int] = Field(default=None, primary_key=True)
    modified: datetime


class SourcesMeta(SQLModel, table=True):
    __tablename__ = "sources_meta"
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(unique=True)
    modified: datetime


class Patient(SQLModel, table=True):
    __tablename__ = "patients"

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

    encounters: List["Encounter"] = Relationship(back_populates="patient")


class Encounter(SQLModel, table=True):
    __tablename__ = "encounters"

    id: Optional[int] = Field(default=None, primary_key=True)
    mrn: int = Field(foreign_key="patients.mrn")
    location: str
    dept: str
    visit_date: date
    visit_time: time
    encounter_type: str
    service_provider: Optional[str] = None
    billing_provider: Optional[str] = None
    with_pcp: Optional[bool] = None
    appt_status: Optional[str] = None
    encounter_diagnoses: Optional[str] = None
    level_of_service: Optional[str] = None

    patient: Optional[Patient] = Relationship(back_populates="encounters")

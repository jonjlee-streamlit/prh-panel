from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional
from datetime import date, datetime


class Meta(SQLModel, table=True):
    __tablename__ = "meta"
    id: Optional[int] = Field(default=None, primary_key=True)
    modified: datetime


class Patient(SQLModel, table=True):
    __tablename__ = "patients"

    prw_id: Optional[int] = Field(default=None, primary_key=True)
    sex: str = Field(regex="^[MFO]$")
    age: Optional[int] = Field(ge=0)
    age_mo: Optional[int] = Field(ge=0)
    age_display: Optional[str] = None
    location: Optional[str] = None
    pcp: Optional[str] = None
    panel_location: Optional[str] = None
    panel_provider: Optional[str] = None

    encounters: List["Encounter"] = Relationship(back_populates="patient")


class Encounter(SQLModel, table=True):
    __tablename__ = "encounters"

    id: Optional[int] = Field(default=None, primary_key=True)
    prw_id: int = Field(foreign_key="patients.prw_id")
    location: str
    encounter_date: date
    encounter_type: str
    service_provider: Optional[str] = None
    with_pcp: Optional[bool] = None
    diagnoses: Optional[str] = None
    level_of_service: Optional[str] = None

    patient: Optional[Patient] = Relationship(back_populates="encounters")

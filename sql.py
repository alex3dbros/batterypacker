import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Table, Float, DateTime, TEXT
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.schema import CreateTable

Base = declarative_base()


class Projects(Base):
    __tablename__ = "Projects"
    ID = Column(Integer, primary_key=True)
    Name = Column(String(150))
    CreationDate = Column(DateTime)
    LastCellNumber = Column(Integer())


class Cells(Base):
    __tablename__ = "Cells"
    ID = Column(Integer, primary_key=True)
    UUID = Column(String(150))
    CellType = Column(String(150))
    ProjectID = Column(Integer())
    Voltage = Column(Float())
    Capacity = Column(Integer())
    ESR = Column(Float())
    Status = Column(String(150))
    AddedDate = Column(DateTime)
    Available = Column(String(150))
    Device = Column(String(150))


class OtherSettings(Base):
    __tablename__ = "OtherSettings"
    ID = Column(Integer, primary_key=True)
    CurrentProjectID = Column(Integer())

engine = create_engine('sqlite:///database.db')

# This is creating the table into the DB
Base.metadata.create_all(engine)

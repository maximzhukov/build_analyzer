from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    
    stages = relationship("Stage", back_populates="project")

class Stage(Base):
    __tablename__ = "stages"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    
    nlp_stage_id = Column(String, index=True) 
    
    
    name = Column(String, nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    target_volume = Column(Float, default=0.0)
    current_volume = Column(Float, default=0.0) 

    project = relationship("Project", back_populates="stages")
    telemetry = relationship("Telemetry", back_populates="stage")

class Telemetry(Base):
    __tablename__ = "telemetry"

    
    id = Column(Integer, primary_key=True, index=True)
    stage_id = Column(Integer, ForeignKey("stages.id"))
    
    
    detected_objects = Column(JSON) 
    
    
    calculated_volume = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    stage = relationship("Stage", back_populates="telemetry")
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Text, Integer, Float, Boolean, JSON, TIMESTAMP
from sqlalchemy.sql import text

Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"
    id = Column(Text, primary_key=True)
    source_url = Column(Text, nullable=False)
    preview_url = Column(Text)
    duration_ms = Column(Integer)
    fps = Column(Float)
    width = Column(Integer)
    height = Column(Integer)
    status = Column(Text, server_default='NEW')
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"
    id = Column(Text, primary_key=True)
    video_id = Column(Text)  # FK declared in migration
    model_version = Column(Text)
    state = Column(Text)
    log = Column(JSON, server_default='[]')
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

class Segment(Base):
    __tablename__ = "segments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Text)  # FK declared in migration
    start_ms = Column(Integer, nullable=False)
    end_ms = Column(Integer, nullable=False)
    move_id = Column(Text, nullable=False)
    confidence = Column(Float)
    mirror = Column(Boolean, server_default=text('false'))
    alts = Column(JSON, server_default='[]')
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

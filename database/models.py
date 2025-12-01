"""
Database models for storing test results in Supabase
"""
from sqlalchemy import create_engine, Column, String, DateTime, JSON, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class TestExecution(Base):
    """Store test execution results"""
    __tablename__ = 'test_executions'
    
    task_id = Column(String(100), primary_key=True)
    test_id = Column(String(100))
    feature_name = Column(String(500))
    status = Column(String(50))  # pending, running, completed, failed
    
    # Test configuration
    specification = Column(JSON)
    configuration = Column(JSON)
    
    # Results
    result = Column(JSON)
    error = Column(Text, nullable=True)
    
    # Summary
    total_scenarios = Column(Integer, default=0)
    passed_scenarios = Column(Integer, default=0)
    failed_scenarios = Column(Integer, default=0)
    pass_rate = Column(String(20), nullable=True)
    
    # Response codes
    response_code = Column(Integer, nullable=True)
    response_status = Column(String(20), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'task_id': self.task_id,
            'test_id': self.test_id,
            'feature_name': self.feature_name,
            'status': self.status,
            'specification': self.specification,
            'configuration': self.configuration,
            'result': self.result,
            'error': self.error,
            'total_scenarios': self.total_scenarios,
            'passed_scenarios': self.passed_scenarios,
            'failed_scenarios': self.failed_scenarios,
            'pass_rate': self.pass_rate,
            'response_code': self.response_code,
            'response_status': self.response_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }


# Database connection
from config import Config
DATABASE_URL = Config.get_database_url()

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    def init_db():
        """Initialize database tables"""
        Base.metadata.create_all(bind=engine)
else:
    engine = None
    SessionLocal = None
    
    def init_db():
        print("Warning: DATABASE_URL not set. Database features disabled.")

"""
Database service for persisting test results
"""
from database.models import TestExecution, SessionLocal, init_db
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger(__name__)


class DatabaseService:
    """Service for database operations"""
    
    @staticmethod
    def save_test_execution(task_id, test_id, feature_name, specification, configuration):
        """Save new test execution"""
        if not SessionLocal:
            logger.warning("Database not configured. Skipping save.")
            return None
            
        try:
            db = SessionLocal()
            
            execution = TestExecution(
                task_id=task_id,
                test_id=test_id,
                feature_name=feature_name,
                status='pending',
                specification=specification,
                configuration=configuration,
                created_at=datetime.utcnow()
            )
            
            db.add(execution)
            db.commit()
            db.refresh(execution)
            
            logger.info(f"Saved test execution: {task_id}")
            return execution.to_dict()
            
        except Exception as e:
            logger.error(f"Error saving test execution: {str(e)}")
            db.rollback()
            return None
        finally:
            db.close()
    
    @staticmethod
    def update_test_status(task_id, status, result=None, error=None):
        """Update test execution status"""
        if not SessionLocal:
            return None
            
        try:
            db = SessionLocal()
            
            execution = db.query(TestExecution).filter(TestExecution.task_id == task_id).first()
            
            if execution:
                execution.status = status
                execution.updated_at = datetime.utcnow()
                
                if result:
                    execution.result = result
                    execution.end_time = datetime.fromisoformat(result.get('end_time')) if result.get('end_time') else None
                    execution.start_time = datetime.fromisoformat(result.get('start_time')) if result.get('start_time') else None
                    
                    # Extract summary
                    summary = result.get('summary', {})
                    execution.total_scenarios = summary.get('total', 0)
                    execution.passed_scenarios = summary.get('passed', 0)
                    execution.failed_scenarios = summary.get('failed', 0)
                    execution.pass_rate = summary.get('pass_rate')
                    
                    # Extract response code from first scenario
                    scenarios = result.get('scenarios', [])
                    if scenarios and scenarios[0].get('steps'):
                        first_step = scenarios[0]['steps'][0]
                        execution.response_code = first_step.get('response_code')
                        execution.response_status = first_step.get('response_status')
                
                if error:
                    execution.error = str(error)
                
                db.commit()
                db.refresh(execution)
                
                logger.info(f"Updated test execution: {task_id} -> {status}")
                return execution.to_dict()
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating test execution: {str(e)}")
            db.rollback()
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_test_execution(task_id):
        """Get test execution by task_id"""
        if not SessionLocal:
            return None
            
        try:
            db = SessionLocal()
            execution = db.query(TestExecution).filter(TestExecution.task_id == task_id).first()
            
            if execution:
                return execution.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Error getting test execution: {str(e)}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_all_test_executions(limit=50):
        """Get all test executions"""
        if not SessionLocal:
            return []
            
        try:
            db = SessionLocal()
            executions = db.query(TestExecution).order_by(TestExecution.created_at.desc()).limit(limit).all()
            
            return [e.to_dict() for e in executions]
            
        except Exception as e:
            logger.error(f"Error getting test executions: {str(e)}")
            return []
        finally:
            db.close()


# Initialize database on import
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")

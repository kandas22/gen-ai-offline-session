"""
Task manager for handling async operations
"""
import uuid
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
from config import Config


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskManager:
    """Manages async tasks and their results"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        Config.ensure_directories()
    
    def create_task(self, task_type: str, data: Optional[Dict] = None) -> str:
        """
        Create a new task
        
        Args:
            task_type: Type of task (e.g., 'search', 'bdd_test')
            data: Optional task data
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            'id': task_id,
            'type': task_type,
            'status': TaskStatus.PENDING.value,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'data': data or {},
            'result': None,
            'error': None
        }
        self._save_task(task_id)
        return task_id
    
    def update_task_status(self, task_id: str, status: TaskStatus, 
                          result: Optional[Any] = None, 
                          error: Optional[str] = None):
        """
        Update task status
        
        Args:
            task_id: Task ID
            status: New status
            result: Task result (if completed)
            error: Error message (if failed)
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        self.tasks[task_id]['status'] = status.value
        self.tasks[task_id]['updated_at'] = datetime.now().isoformat()
        
        if result is not None:
            self.tasks[task_id]['result'] = result
        
        if error is not None:
            self.tasks[task_id]['error'] = error
        
        self._save_task(task_id)
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task by ID
        
        Args:
            task_id: Task ID
            
        Returns:
            Task data or None
        """
        return self.tasks.get(task_id)
    
    def get_task_status(self, task_id: str) -> Optional[str]:
        """
        Get task status
        
        Args:
            task_id: Task ID
            
        Returns:
            Task status or None
        """
        task = self.get_task(task_id)
        return task['status'] if task else None
    
    def get_task_result(self, task_id: str) -> Optional[Any]:
        """
        Get task result
        
        Args:
            task_id: Task ID
            
        Returns:
            Task result or None
        """
        task = self.get_task(task_id)
        return task['result'] if task else None
    
    def _save_task(self, task_id: str):
        """
        Save task to file
        
        Args:
            task_id: Task ID
        """
        task_file = os.path.join(Config.RESULTS_DIR, f'{task_id}.json')
        with open(task_file, 'w') as f:
            json.dump(self.tasks[task_id], f, indent=2)
    
    def load_task(self, task_id: str) -> bool:
        """
        Load task from file
        
        Args:
            task_id: Task ID
            
        Returns:
            True if loaded successfully
        """
        task_file = os.path.join(Config.RESULTS_DIR, f'{task_id}.json')
        if os.path.exists(task_file):
            with open(task_file, 'r') as f:
                self.tasks[task_id] = json.load(f)
            return True
        return False


# Global task manager instance
task_manager = TaskManager()

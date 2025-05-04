"""
Workflow orchestration for POD Automation System.
Manages the execution of workflows and tasks.
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, Union
import threading
import queue

# Import utilities
from pod_automation.utils.logging_config import get_logger
from pod_automation.core.database import get_database

# Initialize logger
logger = get_logger(__name__)

class Task:
    """Represents a task in a workflow."""
    
    def __init__(
        self,
        name: str,
        func: Callable,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
        dependencies: List[str] = None,
        timeout: int = 3600,
        retry_count: int = 3,
        retry_delay: int = 60
    ):
        """Initialize a task.
        
        Args:
            name: Task name
            func: Function to execute
            args: Function arguments
            kwargs: Function keyword arguments
            dependencies: List of task names that must complete before this task
            timeout: Maximum execution time in seconds
            retry_count: Number of retries on failure
            retry_delay: Delay between retries in seconds
        """
        self.name = name
        self.func = func
        self.args = args or []
        self.kwargs = kwargs or {}
        self.dependencies = dependencies or []
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        
        self.status = "pending"
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
        self.attempts = 0
    
    def execute(self, context: Dict[str, Any] = None) -> Any:
        """Execute the task.
        
        Args:
            context: Workflow context
            
        Returns:
            Task result
        """
        if context is None:
            context = {}
        
        self.status = "running"
        self.start_time = datetime.now()
        self.attempts += 1
        
        try:
            # Add context to kwargs
            kwargs = {**self.kwargs, "context": context}
            
            # Execute function
            self.result = self.func(*self.args, **kwargs)
            self.status = "completed"
            logger.info(f"Task '{self.name}' completed successfully")
        except Exception as e:
            self.error = str(e)
            self.status = "failed"
            logger.error(f"Task '{self.name}' failed: {str(e)}")
        
        self.end_time = datetime.now()
        return self.result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary.
        
        Returns:
            Dict containing task data
        """
        return {
            "name": self.name,
            "status": self.status,
            "dependencies": self.dependencies,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "attempts": self.attempts,
            "error": self.error
        }


class Workflow:
    """Represents a workflow of tasks."""
    
    def __init__(
        self,
        name: str,
        description: str = "",
        tasks: List[Task] = None,
        context: Dict[str, Any] = None,
        max_parallel_tasks: int = 4
    ):
        """Initialize a workflow.
        
        Args:
            name: Workflow name
            description: Workflow description
            tasks: List of tasks
            context: Workflow context
            max_parallel_tasks: Maximum number of tasks to execute in parallel
        """
        self.name = name
        self.description = description
        self.tasks = tasks or []
        self.context = context or {}
        self.max_parallel_tasks = max_parallel_tasks
        
        self.id = None
        self.status = "pending"
        self.start_time = None
        self.end_time = None
        self.task_results = {}
        
        # Get database
        self.db = get_database()
    
    def add_task(self, task: Task) -> None:
        """Add a task to the workflow.
        
        Args:
            task: Task to add
        """
        self.tasks.append(task)
    
    def get_task(self, name: str) -> Optional[Task]:
        """Get a task by name.
        
        Args:
            name: Task name
            
        Returns:
            Task if found, None otherwise
        """
        for task in self.tasks:
            if task.name == name:
                return task
        return None
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks that are ready to execute.
        
        Returns:
            List of tasks ready to execute
        """
        ready_tasks = []
        
        for task in self.tasks:
            if task.status == "pending":
                # Check if all dependencies are completed
                dependencies_completed = True
                
                for dep_name in task.dependencies:
                    dep_task = self.get_task(dep_name)
                    
                    if dep_task is None or dep_task.status != "completed":
                        dependencies_completed = False
                        break
                
                if dependencies_completed:
                    ready_tasks.append(task)
        
        return ready_tasks
    
    def execute(self) -> Dict[str, Any]:
        """Execute the workflow.
        
        Returns:
            Dict containing workflow results
        """
        self.status = "running"
        self.start_time = datetime.now()
        
        # Create workflow record in database
        workflow_data = {
            "name": self.name,
            "status": self.status,
            "started_at": self.start_time.isoformat(),
            "metadata": json.dumps({
                "description": self.description,
                "max_parallel_tasks": self.max_parallel_tasks
            })
        }
        
        self.id = self.db.create("workflows", workflow_data)
        
        logger.info(f"Starting workflow '{self.name}' with ID {self.id}")
        
        # Execute tasks
        task_queue = queue.Queue()
        running_tasks = []
        completed_tasks = []
        
        # Add initial ready tasks to queue
        for task in self.get_ready_tasks():
            task_queue.put(task)
        
        while True:
            # Check if all tasks are completed
            if len(completed_tasks) == len(self.tasks):
                break
            
            # Check if there are tasks in the queue and slots available
            while not task_queue.empty() and len(running_tasks) < self.max_parallel_tasks:
                task = task_queue.get()
                
                # Create task record in database
                task_data = {
                    "workflow_id": self.id,
                    "step_name": task.name,
                    "status": "running",
                    "started_at": datetime.now().isoformat()
                }
                
                task_id = self.db.create("workflow_steps", task_data)
                
                # Execute task in a thread
                thread = threading.Thread(
                    target=self._execute_task,
                    args=(task, task_id)
                )
                thread.start()
                
                running_tasks.append((task, thread, task_id))
            
            # Check if any running tasks have completed
            for i, (task, thread, task_id) in enumerate(running_tasks):
                if not thread.is_alive():
                    # Update task record in database
                    task_data = {
                        "status": task.status,
                        "completed_at": task.end_time.isoformat() if task.end_time else None,
                        "result": json.dumps({
                            "result": task.result,
                            "error": task.error
                        })
                    }
                    
                    self.db.update("workflow_steps", task_id, task_data)
                    
                    # Add task result to context
                    self.context[task.name] = task.result
                    self.task_results[task.name] = task.result
                    
                    # Add task to completed tasks
                    completed_tasks.append(task)
                    
                    # Remove task from running tasks
                    running_tasks.pop(i)
                    
                    # Add new ready tasks to queue
                    for ready_task in self.get_ready_tasks():
                        if ready_task not in completed_tasks and ready_task not in [t for t, _, _ in running_tasks]:
                            task_queue.put(ready_task)
                    
                    break
            
            # Sleep to avoid high CPU usage
            time.sleep(0.1)
        
        # Update workflow status
        self.status = "completed"
        self.end_time = datetime.now()
        
        # Check if any tasks failed
        for task in self.tasks:
            if task.status == "failed":
                self.status = "failed"
                break
        
        # Update workflow record in database
        workflow_data = {
            "status": self.status,
            "completed_at": self.end_time.isoformat()
        }
        
        self.db.update("workflows", self.id, workflow_data)
        
        logger.info(f"Workflow '{self.name}' completed with status '{self.status}'")
        
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "tasks": {task.name: task.to_dict() for task in self.tasks},
            "results": self.task_results
        }
    
    def _execute_task(self, task: Task, task_id: int) -> None:
        """Execute a task.
        
        Args:
            task: Task to execute
            task_id: Task ID in database
        """
        # Execute task
        task.execute(self.context)
        
        # Retry on failure
        while task.status == "failed" and task.attempts < task.retry_count:
            logger.info(f"Retrying task '{task.name}' (attempt {task.attempts + 1}/{task.retry_count})")
            
            # Wait before retrying
            time.sleep(task.retry_delay)
            
            # Execute task again
            task.execute(self.context)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary.
        
        Returns:
            Dict containing workflow data
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "tasks": [task.to_dict() for task in self.tasks]
        }


class WorkflowManager:
    """Manages workflows."""
    
    def __init__(self):
        """Initialize workflow manager."""
        self.workflows = {}
        self.db = get_database()
    
    def create_workflow(
        self,
        name: str,
        description: str = "",
        tasks: List[Task] = None,
        context: Dict[str, Any] = None,
        max_parallel_tasks: int = 4
    ) -> Workflow:
        """Create a new workflow.
        
        Args:
            name: Workflow name
            description: Workflow description
            tasks: List of tasks
            context: Workflow context
            max_parallel_tasks: Maximum number of tasks to execute in parallel
            
        Returns:
            Workflow instance
        """
        workflow = Workflow(
            name=name,
            description=description,
            tasks=tasks,
            context=context,
            max_parallel_tasks=max_parallel_tasks
        )
        
        self.workflows[name] = workflow
        return workflow
    
    def get_workflow(self, name: str) -> Optional[Workflow]:
        """Get a workflow by name.
        
        Args:
            name: Workflow name
            
        Returns:
            Workflow if found, None otherwise
        """
        return self.workflows.get(name)
    
    def execute_workflow(self, name: str) -> Dict[str, Any]:
        """Execute a workflow by name.
        
        Args:
            name: Workflow name
            
        Returns:
            Dict containing workflow results
        """
        workflow = self.get_workflow(name)
        
        if workflow:
            return workflow.execute()
        else:
            logger.error(f"Workflow '{name}' not found")
            return {"error": f"Workflow '{name}' not found"}
    
    def get_workflow_status(self, workflow_id: int) -> Dict[str, Any]:
        """Get workflow status by ID.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Dict containing workflow status
        """
        # Get workflow from database
        workflow = self.db.read("workflows", workflow_id)
        
        if workflow:
            # Get workflow steps
            steps = self.db.query(
                "SELECT * FROM workflow_steps WHERE workflow_id = ? ORDER BY id",
                (workflow_id,)
            )
            
            # Add steps to workflow
            workflow["steps"] = steps
            
            return workflow
        else:
            logger.error(f"Workflow with ID {workflow_id} not found")
            return {"error": f"Workflow with ID {workflow_id} not found"}
    
    def list_workflows(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List workflows.
        
        Args:
            limit: Maximum number of workflows to return
            
        Returns:
            List of workflows
        """
        # Get workflows from database
        workflows = self.db.query(
            "SELECT * FROM workflows ORDER BY started_at DESC LIMIT ?",
            (limit,)
        )
        
        return workflows

# Global workflow manager instance
_workflow_manager = None

def get_workflow_manager() -> WorkflowManager:
    """Get global workflow manager instance.
    
    Returns:
        WorkflowManager instance
    """
    global _workflow_manager
    
    if _workflow_manager is None:
        _workflow_manager = WorkflowManager()
    
    return _workflow_manager
#!/usr/bin/env python3
"""
base_agent.py – Diesel-Goose Agent Base Class

Defines the foundation for all autonomous agents in the Greenhead Labs ecosystem.
Provides think/act/remember lifecycle with ethical constraints and delegation protocols.

Author: Diesel Goose – Founder / Chairman
Version: 1.0 – Executable agent framework
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    COMPLETED = "completed"
    ERROR = "error"
    BLOCKED = "blocked"  # Ethical veto

class EthicalLevel(Enum):
    """Ethical classification of tasks."""
    APPROVED = "approved"       # No concerns
    REVIEW = "review"           # Needs human check
    VETO = "veto"               # Blocked - violates principles

@dataclass
class AgentTask:
    """Task definition for agents."""
    task_id: str
    description: str
    priority: int  # 1-10, 10 being highest
    context: Dict[str, Any]
    constraints: List[str]

@dataclass
class AgentResult:
    """Result of agent execution."""
    task_id: str
    status: AgentStatus
    output: Any
    memories: List[Dict[str, Any]]
    ethical_check: EthicalLevel
    execution_time_ms: int

class BaseAgent(ABC):
    """
    Base class for all Diesel-Goose agents.
    
    All agents must implement:
    - think(): Analyze and plan
    - act(): Execute the task
    - remember(): Extract learnings
    
    Agents operate under strict ethical guidelines:
    - Faith-aligned execution
    - Family-first priorities
    - No shortcuts or deception
    - Radical delegation upward on blockers
    """
    
    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.status = AgentStatus.IDLE
        self.memory: List[Dict[str, Any]] = []
        self.task_history: List[str] = []
    
    def execute(self, task: AgentTask) -> AgentResult:
        """
        Main execution pipeline for any task.
        
        Pipeline:
        1. Ethical pre-check
        2. Think (plan)
        3. Act (execute)
        4. Remember (learn)
        5. Return result
        """
        import time
        start_time = time.time()
        
        # Step 1: Ethical check
        ethical_status = self._ethical_check(task)
        if ethical_status == EthicalLevel.VETO:
            return AgentResult(
                task_id=task.task_id,
                status=AgentStatus.BLOCKED,
                output="Task blocked by ethical veto layer",
                memories=[],
                ethical_check=ethical_status,
                execution_time_ms=0
            )
        
        # Step 2: Think
        self.status = AgentStatus.THINKING
        plan = self.think(task)
        
        # Step 3: Act
        self.status = AgentStatus.ACTING
        try:
            output = self.act(task, plan)
            status = AgentStatus.COMPLETED
        except Exception as e:
            output = f"Error: {str(e)}"
            status = AgentStatus.ERROR
        
        # Step 4: Remember
        self.status = AgentStatus.IDLE
        memories = self.remember(task, output)
        
        execution_time = int((time.time() - start_time) * 1000)
        
        # Record in history
        self.task_history.append(task.task_id)
        
        return AgentResult(
            task_id=task.task_id,
            status=status,
            output=output,
            memories=memories,
            ethical_check=ethical_status,
            execution_time_ms=execution_time
        )
    
    def _ethical_check(self, task: AgentTask) -> EthicalLevel:
        """
        Pre-execution ethical validation.
        
        Checks:
        - Against founder principles (faith, family, integrity)
        - Privacy implications
        - Potential harm or deception
        """
        description = task.description.lower()
        constraints = [c.lower() for c in task.constraints]
        
        # Auto-veto patterns
        veto_patterns = [
            "deceive", "lie", "fraud", "steal", "harm",
            "exploit", "manipulate", "mislead"
        ]
        
        for pattern in veto_patterns:
            if pattern in description:
                return EthicalLevel.VETO
        
        # Review required patterns
        review_patterns = [
            "financial", "money", "transaction", "private key",
            "wallet", "secret", "password"
        ]
        
        for pattern in review_patterns:
            if pattern in description:
                return EthicalLevel.REVIEW
        
        # Check constraints for ethical flags
        if "ethical-review" in constraints:
            return EthicalLevel.REVIEW
        
        return EthicalLevel.APPROVED
    
    @abstractmethod
    def think(self, task: AgentTask) -> Dict[str, Any]:
        """
        Analyze task and create execution plan.
        
        Args:
            task: The task to analyze
        
        Returns:
            Dictionary containing plan details
        """
        pass
    
    @abstractmethod
    def act(self, task: AgentTask, plan: Dict[str, Any]) -> Any:
        """
        Execute the task according to plan.
        
        Args:
            task: The original task
            plan: The execution plan from think()
        
        Returns:
            Task output
        """
        pass
    
    @abstractmethod
    def remember(self, task: AgentTask, output: Any) -> List[Dict[str, Any]]:
        """
        Extract learnings from task execution.
        
        Args:
            task: The completed task
            output: The task output
        
        Returns:
            List of memory entries to store
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status.value,
            "task_count": len(self.task_history),
            "recent_tasks": self.task_history[-5:]
        }


# Example concrete agent implementation
class FileEditAgent(BaseAgent):
    """Example agent for file editing tasks."""
    
    def think(self, task: AgentTask) -> Dict[str, Any]:
        """Plan file edit operation."""
        return {
            "action": "edit_file",
            "file_path": task.context.get("file_path"),
            "operation": task.context.get("operation", "modify"),
            "backup": True
        }
    
    def act(self, task: AgentTask, plan: Dict[str, Any]) -> Any:
        """Execute file edit."""
        import shutil
        from pathlib import Path
        
        file_path = Path(plan["file_path"])
        
        if not file_path.exists():
            return f"Error: File not found: {file_path}"
        
        # Create backup
        if plan["backup"]:
            backup_path = file_path.with_suffix(file_path.suffix + ".backup")
            shutil.copy(file_path, backup_path)
        
        # Perform edit (simplified example)
        operation = task.context.get("operation")
        
        if operation == "modify":
            # Actual edit logic would go here
            return f"Modified {file_path}"
        
        return f"Unknown operation: {operation}"
    
    def remember(self, task: AgentTask, output: Any) -> List[Dict[str, Any]]:
        """Extract learnings."""
        return [
            {
                "content": f"Edited file: {task.context.get('file_path')}",
                "confidence": 0.95,
                "category": "action"
            }
        ]


if __name__ == "__main__":
    # Demo
    print("🦆 BaseAgent Framework Demo")
    print("=" * 50)
    
    # Create test agent
    agent = FileEditAgent("file-001", "File Editor")
    
    # Create test task
    task = AgentTask(
        task_id="task-001",
        description="Edit configuration file",
        priority=5,
        context={
            "file_path": "/tmp/test.txt",
            "operation": "modify"
        },
        constraints=["backup-first"]
    )
    
    print(f"Agent: {agent.name}")
    print(f"Task: {task.description}")
    print(f"Ethical check: {agent._ethical_check(task).value}")
    print()
    print("Status:", agent.get_status())

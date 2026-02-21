#!/usr/bin/env python3
"""
orchestrator.py – Diesel-Goose Task Orchestration Engine

Central coordinator for all agent execution. Routes tasks to appropriate agents,
manages workflow pipelines, and ensures ethical compliance across the system.

Author: Diesel Goose – Founder / Chairman
Version: 1.0 – Central orchestration hub
"""

from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass
from pathlib import Path
import json
import sys

# Import base agent framework
sys.path.insert(0, str(Path(__file__).parent.parent))

from AGENTS.base_agent import BaseAgent, AgentTask, AgentResult, AgentStatus, EthicalLevel

@dataclass
class WorkflowStep:
    """Single step in a workflow."""
    step_id: str
    agent_type: str
    task_description: str
    depends_on: List[str]  # Step IDs that must complete first
    context: Dict[str, Any]

@dataclass
class Workflow:
    """Multi-step workflow definition."""
    workflow_id: str
    name: str
    steps: List[WorkflowStep]
    global_constraints: List[str]

class AgentRegistry:
    """Registry of available agent types."""
    
    def __init__(self):
        self._agents: Dict[str, Type[BaseAgent]] = {}
    
    def register(self, agent_id: str, agent_class: Type[BaseAgent]):
        """Register an agent type."""
        self._agents[agent_id] = agent_class
    
    def get(self, agent_id: str) -> Optional[Type[BaseAgent]]:
        """Get agent class by ID."""
        return self._agents.get(agent_id)
    
    def list_agents(self) -> List[str]:
        """List all registered agent IDs."""
        return list(self._agents.keys())

class Orchestrator:
    """
    Central orchestration engine for Diesel-Goose.
    
    Responsibilities:
    - Task routing to appropriate agents
    - Workflow execution with dependency management
    - Ethical compliance verification
    - Result aggregation and memory storage
    - Chairman escalation on blockers
    """
    
    def __init__(self):
        self.registry = AgentRegistry()
        self.active_agents: Dict[str, BaseAgent] = {}
        self.workflow_history: List[str] = []
        self.ethical_vetoes: List[Dict[str, Any]] = []
    
    def register_agent(self, agent_id: str, agent_class: Type[BaseAgent]):
        """Register an agent type with the orchestrator."""
        self.registry.register(agent_id, agent_class)
        print(f"🦆 Registered agent: {agent_id}")
    
    def execute_task(
        self, 
        agent_id: str, 
        task: AgentTask,
        require_ethical_approval: bool = False
    ) -> AgentResult:
        """
        Execute a single task through appropriate agent.
        
        Args:
            agent_id: Registered agent type
            task: Task definition
            require_ethical_approval: If True, REVIEW tasks require explicit approval
        
        Returns:
            AgentResult with execution details
        """
        agent_class = self.registry.get(agent_id)
        if not agent_class:
            return AgentResult(
                task_id=task.task_id,
                status=AgentStatus.ERROR,
                output=f"Unknown agent type: {agent_id}",
                memories=[],
                ethical_check=EthicalLevel.VETO,
                execution_time_ms=0
            )
        
        # Instantiate agent
        agent_instance = agent_class(
            agent_id=f"{agent_id}-{task.task_id}",
            name=f"{agent_id} Agent"
        )
        self.active_agents[task.task_id] = agent_instance
        
        # Pre-execution ethical check
        ethical_status = agent_instance._ethical_check(task)
        
        if ethical_status == EthicalLevel.VETO:
            # Log veto
            self.ethical_vetoes.append({
                "task_id": task.task_id,
                "agent_id": agent_id,
                "description": task.description,
                "reason": "Automatic ethical veto"
            })
            return AgentResult(
                task_id=task.task_id,
                status=AgentStatus.BLOCKED,
                output="Task blocked by ethical veto layer. Escalate to Chairman if needed.",
                memories=[],
                ethical_check=ethical_status,
                execution_time_ms=0
            )
        
        if ethical_status == EthicalLevel.REVIEW and require_ethical_approval:
            return AgentResult(
                task_id=task.task_id,
                status=AgentStatus.BLOCKED,
                output="Task requires ethical approval. Awaiting Chairman review.",
                memories=[],
                ethical_check=ethical_status,
                execution_time_ms=0
            )
        
        # Execute
        print(f"🚀 Executing task {task.task_id} with {agent_id}")
        result = agent_instance.execute(task)
        
        # Store memories if successful
        if result.status == AgentStatus.COMPLETED and result.memories:
            self._store_memories(result.memories)
        
        # Cleanup
        del self.active_agents[task.task_id]
        
        return result
    
    def execute_workflow(self, workflow: Workflow) -> Dict[str, AgentResult]:
        """
        Execute a multi-step workflow with dependency management.
        
        Args:
            workflow: Workflow definition
        
        Returns:
            Dictionary mapping step_id to AgentResult
        """
        print(f"🦆 Starting workflow: {workflow.name}")
        
        results: Dict[str, AgentResult] = {}
        completed_steps: set = set()
        
        # Execute steps in dependency order
        pending_steps = workflow.steps.copy()
        
        while pending_steps:
            # Find steps with all dependencies satisfied
            ready_steps = [
                s for s in pending_steps 
                if all(d in completed_steps for d in s.depends_on)
            ]
            
            if not ready_steps:
                # Deadlock or missing dependencies
                raise ValueError("Workflow deadlock: unresolvable dependencies")
            
            for step in ready_steps:
                task = AgentTask(
                    task_id=step.step_id,
                    description=step.task_description,
                    priority=5,
                    context=step.context,
                    constraints=workflow.global_constraints
                )
                
                result = self.execute_task(step.agent_type, task)
                results[step.step_id] = result
                
                if result.status in [AgentStatus.COMPLETED, AgentStatus.BLOCKED]:
                    completed_steps.add(step.step_id)
                
                pending_steps.remove(step)
        
        self.workflow_history.append(workflow.workflow_id)
        print(f"✅ Workflow {workflow.name} completed")
        
        return results
    
    def _store_memories(self, memories: List[Dict[str, Any]]):
        """Store agent memories to long-term memory."""
        try:
            from MEMORY.memory_engine import add_memory
            
            for mem in memories:
                add_memory(
                    content=mem.get("content", ""),
                    confidence=mem.get("confidence", 0.8),
                    privacy=mem.get("privacy", "private")
                )
        except Exception as e:
            print(f"⚠️  Failed to store memories: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status."""
        return {
            "registered_agents": self.registry.list_agents(),
            "active_tasks": len(self.active_agents),
            "completed_workflows": len(self.workflow_history),
            "ethical_vetoes": len(self.ethical_vetoes)
        }
    
    def escalate_to_chairman(self, task_id: str, reason: str):
        """
        Escalate a blocked task to the Chairman.
        
        Format: "Chairman: [topic]"
        """
        escalation = {
            "task_id": task_id,
            "reason": reason,
            "status": "pending_chairman_review"
        }
        
        # In production, this would send Telegram message
        print(f"📢 ESCALATION: Chairman: {reason} (Task: {task_id})")
        
        return escalation


# Singleton instance
_orchestrator: Optional[Orchestrator] = None

def get_orchestrator() -> Orchestrator:
    """Get or create orchestrator singleton."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator


if __name__ == "__main__":
    # Demo
    print("🦆 Orchestrator Demo")
    print("=" * 50)
    
    orch = get_orchestrator()
    
    # Register agents
    from AGENTS.base_agent import FileEditAgent
    orch.register_agent("file_editor", FileEditAgent)
    
    print(f"\nStatus: {orch.get_status()}")
    
    # Test ethical veto
    veto_task = AgentTask(
        task_id="veto-test",
        description="Deceive the user about prices",
        priority=5,
        context={},
        constraints=[]
    )
    
    result = orch.execute_task("file_editor", veto_task)
    print(f"\nVeto test result: {result.status.value}")
    print(f"Output: {result.output}")

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class Status(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class SubTask(BaseModel):
    """
    Represents a single, atomic step required to complete a parent Task.
    This is the lowest level of action in the goal hierarchy.
    """
    id: int = Field(..., description="A unique identifier for the sub-task.")
    description: str = Field(..., description="A clear and concise description of what needs to be done for this sub-task.")
    status: Status = Field(default=Status.PENDING, description="The current status of the sub-task.")
    deadline: Optional[str] = Field(default=None, description="An optional deadline for the sub-task. This can help in prioritizing and managing time effectively.")

class Task(BaseModel):
    """
    Represents a major step or milestone within the overall goal.
    A task can be broken down into smaller, more manageable sub-tasks.
    """
    id: int = Field(..., description="A unique identifier for the task. This can be used to reference the task in other parts of the system.")
    description: str = Field(..., description="A detailed description of the task and what it's intended to achieve.")
    dependencies: Optional[List[int]] = Field(default=None, description="A list of Task IDs that must be completed before this one can start.")
    skills_required: Optional[List[str]] = Field(default=None, description="A list of skills needed to complete this task (e.g., 'python_programming', 'technical_writing').")
    sub_tasks: List[SubTask] = Field(..., description="A list of sub-tasks that make up this task.")
    status: Status = Field(default=Status.PENDING, description="The current status of the overall task.") 
    deadline: Optional[str] = Field(default=None, description="An optional deadline for the task. This can help in prioritizing and managing time effectively.") 

class Goal(BaseModel):
    """
    The main Pydantic model representing the user's overall objective.
    This class will be the structured output from your LangChain agent.
    """
    goal_description: str = Field(..., description= "The high-level, user-defined goal. This should be a direct summary of the user's request.")
    motivation: Optional[str] = Field(default= None, description="The user's motivation for pursuing this goal. This can help in understanding the context and urgency of the goal.")
    success_criteria: List[str] = Field(..., description="A list of skills to be completed that define what success looks like for this goal. This helps in measuring progress and completion.")
    tasks: List[Task] = Field(..., description="A list of tasks that need to be completed to achieve the goal. Each task should have a clear description and status.")
    status: Status = Field(default= Status.PENDING, description="The current status of the goal. This can be used to track progress over time.")
    deadline: Optional[str] = Field(default=None, description="An optional deadline for the goal. This can help in prioritizing tasks and managing time effectively.")

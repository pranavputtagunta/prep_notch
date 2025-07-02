from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class ScheduleStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class ScheduledSubTask(BaseModel):
    task_id: int = Field(..., description="ID of the parent task.")
    sub_task_id: int = Field(..., description="ID of the sub-task scheduled for this day.")
    description: str = Field(..., description="Description of the sub-task.")
    status: ScheduleStatus = Field(default=ScheduleStatus.PENDING, description="Status of the scheduled sub-task.")

class DaySchedule(BaseModel):
    day: int = Field(..., description="Day number in the schedule (e.g., 1 for Day 1).")
    date: Optional[str] = Field(default=None, description="Optional calendar date for this day (YYYY-MM-DD).")
    scheduled_sub_tasks: List[ScheduledSubTask] = Field(..., description="List of sub-tasks scheduled for this day.")
    notes: Optional[str] = Field(default=None, description="Optional notes or reminders for this day.")

class GoalSchedule(BaseModel):
    goal_description: str = Field(..., description="Description of the goal this schedule is for.")
    total_days: int = Field(..., description="Total number of days in the schedule.")
    day_schedules: List[DaySchedule] = Field(..., description="List of day-by-day schedules.")
    status: ScheduleStatus = Field(default=ScheduleStatus.PENDING, description="Overall status of the schedule.")
    deadline: Optional[str] = Field(default=None, description="Deadline for the overall goal (YYYY-MM-DD).")

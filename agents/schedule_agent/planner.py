from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from schedule.schedule import GoalSchedule
import dotenv
import os
import json

dotenv.load_dotenv()

router = APIRouter()

# Load system message
with open("agents/scheduler_planner.txt", "r") as file:
    system_message = file.read()

# Initialize the LLM
model = ChatGoogleGenerativeAI(
    model = "gemini-2.0-flash",
    temperature = 0.5,
)

# Output parser for GoalSchedule
pydantic_parser = PydanticOutputParser(pydantic_object=GoalSchedule)
format_instructions = pydantic_parser.get_format_instructions()

class ScheduleRequest(BaseModel):
    goal: dict  # Accepts the Goal as a dict (can be improved to use Goal model directly)

@router.post("/plan_schedule", response_model=GoalSchedule)
def plan_schedule(req: ScheduleRequest):
    """Take a structured goal and return a schedule."""
    prompt = ChatPromptTemplate.from_template(template=system_message)
    messages = prompt.format_messages(goals=json.dumps(req.goal), format_instructions=format_instructions)
    response = model.invoke(messages)
    try:
        schedule = pydantic_parser.parse(response.content)
        return schedule
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse schedule: {e}") 
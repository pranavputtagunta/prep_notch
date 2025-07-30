from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from goals import Goal
import dotenv
import os

dotenv.load_dotenv()

router = APIRouter()

# Load system message
with open("/home/prana/prep_notch_src/agents/goal_structurer_config.txt", "r") as file:
    system_message = file.read()

# Initialize the LLM
model = ChatGoogleGenerativeAI(
    model = "gemini-2.0-flash",
    temperature = 0.5,
)

# Output parser for Goal
pydantic_parser = PydanticOutputParser(pydantic_object=Goal)
format_instructions = pydantic_parser.get_format_instructions()

class GoalSummaryRequest(BaseModel):
    summary: str

@router.post("/structure_goal", response_model=Goal)
def structure_goal(req: GoalSummaryRequest):
    """Take a goal summary and return a structured Goal object."""
    prompt = ChatPromptTemplate.from_template(template=system_message)
    messages = prompt.format_messages(summary=req.summary, format_instructions=format_instructions)
    response = model.invoke(messages)
    try:
        goal = pydantic_parser.parse(response.content)
        return goal
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse goal: {e}") 
import dotenv
import os
from sys import exit
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate

from schedule import GoalSchedule, DaySchedule, ScheduledSubTask, ScheduleStatus

dotenv.load_dotenv()

# Load environment variables from .env file
dotenv.load_dotenv()

# Initialize the Google Generative AI model
model = ChatGoogleGenerativeAI(
    model = "gemini-2.0-flash",
    temperature = 0.5,
) # Set more config here or maybe in separate file

if os.path.exists("outputs/goal.json"):
    with open("outputs/goal.json", "r") as file:
        goals = json.load(file)
else:
    print("goal structurer must be run first")
    exit()

with open("agents/scheduler_planner.txt", "r") as file:
    system_message = file.read()

pydantic_parser = PydanticOutputParser(pydantic_object=GoalSchedule)
format_instructions = pydantic_parser.get_format_instructions()

prompt = ChatPromptTemplate.from_template(template= system_message)

messages = prompt.format_messages(goals= json.dumps(goals), format_instructions= format_instructions)

# Parse into goals
response = model.invoke(messages)

goal = pydantic_parser.parse(response.content)

with open("outputs/schedule.json", "w") as f:
    json.dump(goal.model_dump(), f, indent= 4)
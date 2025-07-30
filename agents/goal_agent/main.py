from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers import PydanticOutputParser
from goals import Goal
import uuid
from structurer import router as structurer_router

# Load environment variables from .env file
dotenv.load_dotenv()

app = FastAPI(title="Goal Agent API")

# In-memory session store (for demo; use persistent store in prod)
sessions: Dict[str, dict] = {}

# Load system prompt
with open("/home/prana/prep_notch_src/agents/goal_planner_config.txt", "r") as file:
    system_message = file.read()

prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_message),
    MessagesPlaceholder(variable_name="messages")
])

# Initialize the LLM
model = ChatGoogleGenerativeAI(
    model = "gemini-2.0-flash",
    temperature = 0.5,
)

# Output parser for Goal
pydantic_parser = PydanticOutputParser(pydantic_object=Goal)
format_instructions = pydantic_parser.get_format_instructions()

# --- API Models ---
class UserMessage(BaseModel):
    session_id: str
    message: str

class StartSessionResponse(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    message: str
    information_complete: bool = False
    goal: Optional[Goal] = None

@app.get("/health")
def health_check():
    return {"status": "ok", "agent": "goal"}

@app.post("/start", response_model=StartSessionResponse)
def start_session():
    """Start a new goal planning session."""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"messages": []}
    # Initial system message
    return StartSessionResponse(session_id=session_id, message="Goal planning session started. Please describe your goal.")

@app.post("/chat", response_model=ChatResponse)
def chat_with_agent(user_msg: UserMessage):
    """Send a message to the goal planning agent and get a response."""
    session = sessions.get(user_msg.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    # Add user message
    session["messages"].append(HumanMessage(user_msg.message))
    # Build prompt
    prompt = prompt_template.invoke({"messages": session["messages"]})
    response = model.invoke(prompt)
    session["messages"].append(response)
    text = response.content
    # Check for completion
    if "INFORMATION_COMPLETE" in text:
        # Try to parse the structured goal from the response
        try:
            # Extract only the JSON part after INFORMATION_COMPLETE
            info = text.split("INFORMATION_COMPLETE", 1)[-1].strip()
            # Use the output parser to parse the goal
            goal = pydantic_parser.parse(info)
            session["goal"] = goal
            return ChatResponse(session_id=user_msg.session_id, message="Goal information complete.", information_complete=True, goal=goal)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse goal: {e}")
    return ChatResponse(session_id=user_msg.session_id, message=text)

@app.get("/goal/{session_id}", response_model=Goal)
def get_goal(session_id: str):
    """Get the structured goal for a session (if complete)."""
    session = sessions.get(session_id)
    if not session or "goal" not in session:
        raise HTTPException(status_code=404, detail="Goal not found or not complete.")
    return session["goal"]

app.include_router(structurer_router, prefix="/structurer")

import dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Load environment variables from .env file
dotenv.load_dotenv()

# Initialize the Google Generative AI model
model = ChatGoogleGenerativeAI(
    model = "gemini-2.0-flash",
    temperature = 0.5,
) # Set more config here or maybe in separate file

with open("agents/goal_planner_config.txt", "r") as file:
    system_message = file.read()

workflow = StateGraph(state_schema=MessagesState)

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            system_message
        ),
        MessagesPlaceholder(variable_name="messages")
    ]
)

def call_model(state: MessagesState):
    prompt = prompt_template.invoke(state)
    response = model.invoke(prompt)
    return {"messages": response}

workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory) 
config = {"configurable": {"thread_id": "abc123"}} # random thread id

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Exiting the goal planner. Goodbye!")
        break

    input_messages = [HumanMessage(user_input)]
    output = app.invoke({"messages": input_messages}, config)

    text = output["messages"][-1].content
    if "INFORMATION_COMPLETE" in text: 
        with open("outputs/goals_summary.txt", "w") as f:
            f.write(text)
        break

    output["messages"][-1].pretty_print()

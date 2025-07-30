from fastapi import FastAPI
from .planner import router as planner_router

app = FastAPI(title="Schedule Agent API")

app.include_router(planner_router, prefix="/planner")

@app.get("/health")
def health_check():
    return {"status": "ok", "agent": "schedule"}

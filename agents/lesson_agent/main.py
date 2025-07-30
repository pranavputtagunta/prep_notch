from fastapi import FastAPI

app = FastAPI(title="Lesson Agent API")

@app.get("/health")
def health_check():
    return {"status": "ok", "agent": "lesson"}

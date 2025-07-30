from fastapi import FastAPI

app = FastAPI(title="Prompt Management Agent API")

@app.get("/health")
def health_check():
    return {"status": "ok", "agent": "prompt_management"}

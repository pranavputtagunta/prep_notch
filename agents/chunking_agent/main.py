from fastapi import FastAPI

app = FastAPI(title="Chunking Agent API")

@app.get("/health")
def health_check():
    return {"status": "ok", "agent": "chunking"}

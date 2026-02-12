from fastapi import FastAPI

app = FastAPI(title="Enterprise AI Assistant")

@app.get("/")
def root():
    return {"status": "running"}

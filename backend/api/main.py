from security.auth.models import users_db
from security.auth.auth_handler import create_token
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from rag.query.chat_api import router as chat_router

app = FastAPI(
    title="Enterprise AI Assistant",
    swagger_ui_parameters={"persistAuthorization": True}
)
security = HTTPBearer()

app.include_router(chat_router)

@app.get("/")
def root():
    return {"status": "running"}
@app.post("/login")
def login(username: str, password: str):
    user = users_db.get(username)

    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(username, user["role"])
    return {"access_token": token}
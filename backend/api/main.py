from security.auth.models import users_db
from security.auth.auth_handler import create_token
from fastapi import FastAPI, HTTPException
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware # Added this
from rag.query.chat_api import router as chat_router

app = FastAPI(
    title="Enterprise AI Assistant",
    swagger_ui_parameters={"persistAuthorization": True}
)

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows your Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],  # Allows POST, GET, etc.
    allow_headers=["*"],  # Allows Authorization and Content-Type headers
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
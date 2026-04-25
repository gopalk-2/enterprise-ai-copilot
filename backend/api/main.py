from security.auth.models import users_db
from security.auth.auth_handler import create_token
from fastapi import FastAPI, HTTPException, Response, Depends
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import bcrypt
from rag.query.chat_api import router as chat_router
from api.eval_router import router as eval_router
from memory.sqlite_memory import init_db
from observability.tracing import init_tracing

init_db()
init_tracing()  # OpenTelemetry → Jaeger (graceful no-op if Jaeger is unavailable)
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
app.include_router(eval_router)

@app.get("/")
def root():
    return {"status": "running"}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(request: LoginRequest, response: Response):
    user = users_db.get(request.username)

    if not user or not bcrypt.checkpw(request.password.encode('utf-8'), user["password"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(request.username, user["role"])
    
    # Store token in HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False # Set True in production
    )
    return {"message": "Login successful"}
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

users_db = {
    "admin": {
        "password": hash_password("admin123"), # Store hashed in memory for this mock setup
        "role": "admin"
    },
    "employee": {
        "password": hash_password("emp123"),
        "role": "employee"
    }
}

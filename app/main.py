import os
import psycopg2
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

DATABASE_URL = os.getenv('DATABASE_URL')


# Enable CORS (same as Flask CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get database URL from Railway
DATABASE_URL = os.getenv('DATABASE_URL')

@app.get("/")
def home():
    return {"message": "Hello from FastAPI on Railway!"}

@app.get("/get_user")
def get_user(email: str = Query(..., description="User's email")):
    """Fetch user data by email."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('SELECT id, email FROM "user" WHERE email = %s;', (email,))
    user_info = cur.fetchone()
    cur.close()
    conn.close()

    if user_info:
        return {"id": user_info[0], "email": user_info[1]}
    else:
        raise HTTPException(status_code=404, detail="User not found")

# Run with: uvicorn app:app --host 0.0.0.0 --port 8000
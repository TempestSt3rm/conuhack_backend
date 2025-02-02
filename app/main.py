import os
import psycopg2
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI()

DATABASE_URL = os.getenv('DATABASE_URL')
print(DATABASE_URL) 

# Enable CORS (same as Flask CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Hello from FastAPI on Railway!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/get_user")
def get_user(email: str = Query(..., description="User's email")):
    """Fetch user data by email."""
    try:
        conn = psycopg2.connect(DATABASE_URL)  # Connects to the database
        cur = conn.cursor()  # Create a cursor to interact with the database
        cur.execute('SELECT id, email FROM "user" WHERE email = %s;', (email,))  # Query the database
        user_info = cur.fetchone()  # Get the first record (if any)
        cur.close()
        conn.close()  # Close the database connection

        if user_info:
            return {"id": user_info[0], "email": user_info[1]}  # Return user data
        else:
            raise HTTPException(status_code=404, detail="User not found")
    
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

# Run with: uvicorn app:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    uvicorn.run(app)
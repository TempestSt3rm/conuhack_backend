import os
import psycopg2
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI()

DATABASE_URL = os.getenv('DATABASE_PUBLIC_URL')

# Enable CORS (same as Flask CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    name: str
    email: str


# Category Pydantic model
class Category(BaseModel):
    id: int
    name: str

CATEGORY_DICT = {1:"essentials",2:"discretionary",3:"debt_payment",4:"investment",5:"miscallaneous",6:"saving",7:"income"}
REVERSE_CATEGORY_DICT = {v: k for k, v in CATEGORY_DICT.items()}


# Home endpoint
@app.get("/")
def home():
    return {"message": "Hello from FastAPI!"}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# CRUD for users
@app.get("/users/get_user")
def get_user(email: str = Query(..., description="User's email")):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('SELECT id, name, email FROM "users" WHERE email = %s;', (email,))
        user_info = cur.fetchone()
        cur.close()
        conn.close()

        if user_info:
            return {"id": user_info[0], "name": user_info[1], "email": user_info[2]}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@app.post("/users/add_user")
def add_user(user: User):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO "users" (name, email) VALUES (%s, %s) RETURNING id;',
            (user.name, user.email)
        )
        user_id = cur.fetchone()[0]  # Get the generated ID
        conn.commit()
        cur.close()
        conn.close()
        return {"id": user_id, "name": user.name, "email": user.email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.get("/users/get_all_users")
def get_all_users():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('SELECT id, name, email FROM "users";')
        users = cur.fetchall()
        cur.close()
        conn.close()

        if users:
            return [{"id": user[0], "name": user[1], "email": user[2]} for user in users]
        else:
            return {"message": "No users found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.delete("/users/delete_user")
def delete_user(email: str = Query(..., description="Email of the user to delete")):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('DELETE FROM "users" WHERE email = %s RETURNING id, name, email;', (email,))
        user_info = cur.fetchone()
        if user_info:
            conn.commit()
            cur.close()
            conn.close()
            return {"message": f"User with email {email} has been deleted.", "user": {"id": user_info[0], "name": user_info[1], "email": user_info[2]}}
        else:
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


# CRUD for categories
@app.post("/categories/add_category")
def add_category(category: Category):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('INSERT INTO "categories" (name) VALUES (%s) RETURNING id;', 
                    (category.name,))
        category_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return {"id": category_id, "name": category.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.get("/categories/get_all_categories")
def get_all_categories():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('SELECT id, name FROM "categories";')
        categories = cur.fetchall()
        cur.close()
        conn.close()

        if categories:
            return [{"id": category[0], "name": category[1]} for category in categories]
        else:
            return {"message": "No categories found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.delete("/categories/delete_category")
def delete_category(id: int = Query(..., description="ID of the category to delete")):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('DELETE FROM "categories" WHERE id = %s RETURNING id, name;', (id,))
        category_info = cur.fetchone()
        if category_info:
            conn.commit()
            cur.close()
            conn.close()
            return {"message": f"Category with ID {id} has been deleted.", "category": {"id": category_info[0], "name": category_info[1]}}
        else:
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Category not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


from pydantic import BaseModel
from typing import Optional

class Transaction(BaseModel):
    user_id: int
    date: str  # Use datetime.date if necessary
    amount: float
    category_id: int
    source: str
    recurring : Optional[str]

class AddedTransaction(BaseModel):
    user_id: int
    date: str  # Use datetime.date if necessary
    amount: float
    category: str
    source: str
    recurring : Optional[str]


# Add Transaction
@app.post("/transactions/add_transaction")
def add_transaction(transaction: AddedTransaction):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO "transactions" (user_id, date, amount, category_id, source) '
            'VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;',
            (transaction.user_id, transaction.date, transaction.amount, 
             REVERSE_CATEGORY_DICT[transaction.category], transaction.source, transaction.recurring)
        )
        transaction_id = cur.fetchone()[0]  # Get the auto-generated ID
        conn.commit()
        cur.close()
        conn.close()
        return {
            "id": transaction_id,  # Return the newly generated ID
            "user_id": transaction.user_id,
            "date": transaction.date,
            "amount": transaction.amount,
            "category_id": REVERSE_CATEGORY_DICT[transaction.category_id],
            "source": transaction.source,
            "recurring" : transaction.recurring
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


# Get All Transactions by user_id
@app.get("/transactions/get_transactions_by_user")
def get_transactions_by_user(user_id: int):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('''
            SELECT id, user_id, date, amount, category_id, source, recurring
            FROM "transactions"
            WHERE user_id = %s;
        ''', (user_id,))
        
        transactions = cur.fetchall()
        cur.close()
        conn.close()

        if transactions:
            
            return [{
                "id": t[0], "date": t[2], "amount": t[3], 
                "category": CATEGORY_DICT[t[4]], "description": t[5], "recurring": t[6], 
                "type": "income" if t[3] >= 0 else "expense"
                } for t in transactions]
        else:
            return {"message": f"No transactions found for user_id {user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


# Get All Transactions
@app.get("/transactions/get_all_transactions")
def get_all_transactions():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('SELECT id, user_id, date, amount, category_id, source, recurring FROM "transactions";')
        transactions = cur.fetchall()
        cur.close()
        conn.close()

        if transactions:
            return [{"id": t[0], "user_id": t[1], "date": t[2], "amount": t[3], 
                     "category": CATEGORY_DICT[t[4]], "source": t[5], "recurring": t[6]} for t in transactions]
        else:
            return {"message": "No transactions found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

# Delete Transaction
@app.delete("/transactions/delete_transaction")
def delete_transaction(id: int = Query(..., description="ID of the transaction to delete")):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            'DELETE FROM "transactions" WHERE id = %s RETURNING id, user_id, date, amount, category_id, source, recurring;',
            (id,))
        transaction_info = cur.fetchone()
        if transaction_info:
            conn.commit()
            cur.close()
            conn.close()
            return {"message": f"Transaction with ID {id} has been deleted.", 
                    "transaction": {"id": transaction_info[0], "user_id": transaction_info[1], "date": transaction_info[2],
                                    "amount": transaction_info[3], "category_id": transaction_info[4],
                                    "source": transaction_info[5], "recurring": transaction_info[6]}}
        else:
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Transaction not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.put("/transactions/update_transaction")
def update_transaction(id: int, transaction: Transaction):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Check if the transaction exists
        cur.execute('SELECT id FROM "transactions" WHERE id = %s;', (id,))
        existing_transaction = cur.fetchone()
        
        if not existing_transaction:
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Update the transaction
        cur.execute('''
            UPDATE "transactions"
            SET user_id = %s, date = %s, amount = %s, category_id = %s, source = %s, recurring = %s
            WHERE id = %s RETURNING id, user_id, date, amount, category_id, source, recurring;
        ''', (transaction.user_id, transaction.date, transaction.amount, transaction.category_id, 
              transaction.source, transaction.recurring, id))
        
        updated_transaction = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "id": updated_transaction[0],
            "user_id": updated_transaction[1],
            "date": updated_transaction[2],
            "amount": updated_transaction[3],
            "category_id": updated_transaction[4],
            "source": updated_transaction[5],
            "recurring": updated_transaction[6]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    
@app.get("/verify_user")
def verify_user(email: str):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        print("before")

        cur.execute('''
        SELECT id,email,name FROM users 
        WHERE email = %s LIMIT 1;
        ''', (email,))
        
        result = cur.fetchall()  # Get a single row (tuple) instead of fetchall()
        print(result)
        cur.close()
        conn.close()

        if result:
            return {"isValid":True,"id": result[0][0],"email": result[0][1],"name": result[0][2] }  # Return user_id if found
        else:
            return {"isValid":True,"username": None }  # Return None if email not found

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Run with: uvicorn app:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    uvicorn.run(app)

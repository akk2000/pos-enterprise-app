import os
import psycopg2
from pydantic import BaseModel
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="POS Enterprise API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "posdb")
DB_USER = os.getenv("DB_USER", "posuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "possecret")

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

class CartItem(BaseModel):
    id: int
    name: str
    price: float
    quantity: int

class OrderPayload(BaseModel):
    items: List[CartItem]
    total: float


# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Welcome to POS Backend API connected to DB!"}

@app.get("/products")
def get_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price FROM products;")
        rows = cursor.fetchall()
        
        products = [{"id": row[0], "name": row[1], "price": float(row[2])} for row in rows]
        
        cursor.close()
        conn.close()
        return products
    except Exception as e:
        return {"error": str(e)}

@app.post("/orders")
def create_order(payload: OrderPayload):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO orders (total_amount) VALUES (%s) RETURNING id;",
            (payload.total,)
        )
        order_id = cursor.fetchone()[0]
        
        for item in payload.items:
            cursor.execute(
                """
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s);
                """,
                (order_id, item.id, item.quantity, item.price)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"status": "success", "message": "Order saved successfully!", "order_id": order_id}
        
    except Exception as e:
        if 'conn' in locals() and conn:
            conn.rollback()  
        return {"status": "error", "message": str(e)}
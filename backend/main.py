import os
import psycopg2
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
        
        products = [{"id": row[0], "name": row[1], "price": float(row[2])} for rows in [rows] for row in rows]
        
        cursor.close()
        conn.close()
        return products
    except Exception as e:
        return {"error": str(e)}
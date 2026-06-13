from fastapi import FastAPI

app = FastAPI(title="POS Enterprise API")

@app.get("/")
def read_root():
    return {"message": "Welcome to POS Backend API - Hello World"}

@app.get("/products")
def get_products():
    return [
        {"id": 1, "name": "Coffee", "price": 3.50},
        {"id": 2, "name": "Burger", "price": 5.99}
    ]
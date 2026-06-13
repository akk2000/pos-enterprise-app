from fastapi import FastAPI

app = FastAPI(title="POS Enterprise API")

@app.get("/")
def read_root():
    return {"message": "Welcome to POS Backend API - Hello World"}

@app.get("/products")
def get_products():
    # ဒါက နောက်ပိုင်း DB နဲ့ ချိတ်ရင် Dynamic ဖြစ်သွားမယ့် Static data အစမ်းပါ
    return [
        {"id": 1, "name": "Coffee", "price": 3.50},
        {"id": 2, "name": "Burger", "price": 5.99}
    ]
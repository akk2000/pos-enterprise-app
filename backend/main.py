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

        class CartItem(BaseModel):
    id: int
    name: str
    price: float
    quantity: int

class OrderPayload(BaseModel):
    items: List[CartItem]
    total: float

# 3. အောက်ဆုံးမှာ ဒီ Checkout API Endpoint အသစ်ကို ထည့်ပါ
@app.post("/orders")
def create_order(payload: OrderPayload):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # အဆင့် (က) - orders table ထဲကို စုစုပေါင်း ကျသင့်ငွေ အရင်သွင်းပြီး ရလာတဲ့ order_id ကို ယူမယ်
        cursor.execute(
            "INSERT INTO orders (total_amount) VALUES (%s) RETURNING id;",
            (payload.total,)
        )
        order_id = cursor.fetchone()[0]
        
        # အဆင့် (ခ) - ပစ္စည်းတစ်ခုချင်းစီကို order_items table ထဲ ပတ်သွင်းမယ်
        for item in payload.items:
            cursor.execute(
                """
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s);
                """,
                (order_id, item.id, item.quantity, item.price)
              )
        
        # အားလုံး အဆင်ပြေမှ DB ထဲ အတည်ပြု (Commit) လုပ်မယ်
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"status": "success", "message": "Order saved successfully!", "order_id": order_id}
        
    except Exception as e:
        if 'conn' in locals() and conn:
            conn.rollback() # Error တက်ရင် ဒေတာ ပေပွမကျန်ခဲ့အောင် ပြန်ဖျက်တာ (Rollback) ပါ
        return {"status": "error", "message": str(e)}
🛠️ Step 3: Frontend UI တွင် အရေအတွက် တိုး/လျော့ နှင့် တကယ့် Checkout Function ထည့်ခြင်း
အခု Frontend UI ကို အရေအတွက် + / - လုပ်လို့ရအောင် ပြင်ပြီး၊ Checkout နှိပ်ရင် Static alert ပြမယ့်အစား တကယ့် API ဆီ Data လှမ်းပစ်ခိုင်းပါမယ်။

မင်းရဲ့ frontend/src/App.jsx ဖိုင်တစ်ခုလုံးကို အောက်က Production-grade ကုဒ်နဲ့ အစားထိုးလိုက်ပါ-

JavaScript
import { useState, useEffect } from 'react';

function App() {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/products')
      .then((res) => res.json())
      .then((data) => {
        if (!data.error) setProducts(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching products:", err);
        setLoading(false);
      });
  }, []);

  // Cart ထဲ ထည့်တဲ့အခါ ပစ္စည်းရှိပြီးသားဆိုရင် quantity ကို +1 တိုးမယ်
  const addToCart = (product) => {
    const existingItem = cart.find(item => item.id === product.id);
    if (existingItem) {
      setCart(cart.map(item => item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item));
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
  };

  // အရေအတွက် လျှော့တာ သို့မဟုတ် Cart ထဲက ဖျက်တာ
  const updateQuantity = (id, amount) => {
    const targetItem = cart.find(item => item.id === id);
    if (targetItem.quantity === 1 && amount === -1) {
      setCart(cart.filter(item => item.id !== id));
    } else {
      setCart(cart.map(item => item.id === id ? { ...item, quantity: item.quantity + amount } : item));
    }
  };

  const totalInvoiced = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  // တကယ့် Backend API ဆီ အော်ဒါဒေတာ ပို့မယ့် Function
  const handleCheckout = async () => {
    if (cart.length === 0) return;

    const orderPayload = {
      items: cart,
      total: totalInvoiced
    };

    try {
      const response = await fetch('http://127.0.0.1:8000/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderPayload)
      });
      const result = await response.json();
      
      if (result.status === "success") {
        alert(`🎉 Order Placed Successfully! Voucher ID: #${result.order_id}`);
        setCart([]); // အော်ဒါအောင်မြင်ရင် Cart ကို ရှင်းမယ်
      } else {
        alert(`❌ Error: ${result.message}`);
      }
    } catch (error) {
      alert("❌ Failed to connect to Backend Server");
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      <header style={{ textAlign: 'center', marginBottom: '30px' }}>
        <h1 style={{ color: '#333' }}>🏪 Enterprise POS System</h1>
        <p style={{ color: '#666' }}>Real-time 3-Tier Database Transaction Enabled</p>
      </header>

      <div style={{ display: 'flex', gap: '20px' }}>
        {/* ဘယ်ဘက်ခြမ်း: Menu */}
        <div style={{ flex: 2 }}>
          <h2 style={{ color: '#333', marginBottom: '20px' }}>🍕 Menu Items (From Database)</h2>
          {loading ? <p>Loading menu...</p> : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '15px' }}>
              {products.map((product) => (
                <div key={product.id} style={{ border: '1px solid #ddd', padding: '15px', borderRadius: '8px', backgroundColor: '#fff', textAlign: 'center', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                  <h3 style={{ color: '#333' }}>{product.name}</h3>
                  <p style={{ fontWeight: 'bold', color: '#2ecc71' }}>${product.price.toFixed(2)}</p>
                  <button onClick={() => addToCart(product)} style={{ backgroundColor: '#3498db', color: '#fff', border: 'none', padding: '8px 12px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
                    Add to Order
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ညာဘက်ခြမ်း: Current Order */}
        <div style={{ flex: 1, backgroundColor: '#fff', padding: '20px', borderRadius: '8px', border: '1px solid #ddd', height: 'fit-content', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
          <h2 style={{ color: '#333', marginBottom: '20px' }}>🛒 Current Order</h2>
          {cart.length === 0 ? <p style={{ color: '#999' }}>No items added yet.</p> : (
            <div>
              <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                {cart.map((item) => (
                  <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: '1px solid #eee' }}>
                    <div>
                      <span style={{ fontWeight: 'bold', color: '#333' }}>{item.name}</span>
                      <br />
                      <span style={{ fontSize: '0.9rem', color: '#888' }}>${item.price.toFixed(2)} x {item.quantity}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <button onClick={() => updateQuantity(item.id, -1)} style={{ padding: '2px 8px', backgroundColor: '#e74c3c', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>-</button>
                      <span style={{ fontWeight: 'bold', color: '#333' }}>{item.quantity}</span>
                      <button onClick={() => updateQuantity(item.id, 1)} style={{ padding: '2px 8px', backgroundColor: '#2ecc71', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>+</button>
                    </div>
                  </div>
                ))}
              </div>
              <hr style={{ border: '0', borderTop: '1px solid #ddd', margin: '20px 0' }} />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 'bold', fontSize: '1.3rem', margin: '20px 0' }}>
                <span style={{ color: '#333' }}>Total:</span>
                <span style={{ color: '#e74c3c' }}>${totalInvoiced.toFixed(2)}</span>
              </div>
              <button onClick={handleCheckout} style={{ width: '100%', backgroundColor: '#2ecc71', color: '#fff', border: 'none', padding: '12px', borderRadius: '4px', fontSize: '1.1rem', cursor: 'pointer', fontWeight: 'bold', boxShadow: '0 4px 6px rgba(46,204,113,0.2)' }}>
                Place Order (Checkout)
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
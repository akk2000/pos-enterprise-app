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

  const addToCart = (product) => {
    setCart([...cart, product]);
  };

  const totalInvoiced = cart.reduce((sum, item) => sum + item.price, 0);

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      <header style={{ textAlign: 'center', marginBottom: '30px' }}>
        <h1 style={{ color: '#333' }}>🏪 Enterprise POS System</h1>
        <p style={{ color: '#666' }}>Powered by Docker Compose & GitHub Actions</p>
      </header>

      <div style={{ display: 'flex', gap: '20px' }}>
        {}
        <div style={{ flex: 2 }}>
          <h2 style={{ color: '#333', marginBottom: '20px' }}>🍕 Menu Items (From Database)</h2>
          {loading ? <p>Loading menu...</p> : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: '15px' }}>
              {products.map((product) => (
                <div key={product.id} style={{ border: '1px solid #ddd', padding: '15px', borderRadius: '8px', backgroundColor: '#fff', textAlign: 'center', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                  <h3>{product.name}</h3>
                  <p style={{ fontWeight: 'bold', color: '#2ecc71' }}>${product.price.toFixed(2)}</p>
                  <button onClick={() => addToCart(product)} style={{ backgroundColor: '#3498db', color: '#fff', border: 'none', padding: '8px 12px', borderRadius: '4px', cursor: 'pointer' }}>
                    Add to Order
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {}
        <div style={{ flex: 1, backgroundColor: '#fff', padding: '20px', borderRadius: '8px', border: '1px solid #ddd', height: 'fit-content', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
          <h2 style={{ color: '#333', marginBottom: '20px' }}>🛒 Current Order</h2>
          {cart.length === 0 ? <p style={{ color: '#999' }}>No items added yet.</p> : (
            <div>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {cart.map((item, index) => (
                  <li key={index} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #eee' }}>
                    <span>{item.name}</span>
                    <span>${item.price.toFixed(2)}</span>
                  </li>
                ))}
              </ul>
              <hr />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 'bold', fontSize: '1.2rem', margin: '20px 0' }}>
                <span>Total:</span>
                <span style={{ color: '#e74c3c' }}>${totalInvoiced.toFixed(2)}</span>
              </div>
              <button onClick={() => { alert('Order Placed Successfully!'); setCart([]); }} style={{ width: '100%', backgroundColor: '#2ecc71', color: '#fff', border: 'none', padding: '12px', borderRadius: '4px', fontSize: '1rem', cursor: 'pointer', fontWeight: 'bold' }}>
                Checkout
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
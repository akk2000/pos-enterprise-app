CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);


CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    total_amount DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id) ON DELETE CASCADE,
    product_id INT REFERENCES products(id),
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

TRUNCATE TABLE order_items, orders, products RESTART IDENTITY CASCADE;

INSERT INTO products (name, price) VALUES 
('Burger', 5.99),
('Coffee', 3.50),
('Fried Chicken', 7.25);
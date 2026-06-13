CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price NUMERIC(10, 2) NOT NULL
);

INSERT INTO products (name, price) VALUES 
('Burger', 5.99),
('Coffee', 3.50),
('Fried Chicken', 7.25)
ON CONFLICT DO NOTHING;
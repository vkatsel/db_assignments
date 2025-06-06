CREATE DATABASE assignment3;
USE assignment3;

CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    status VARCHAR(20),
    total_amount DECIMAL(10,2)
);

INSERT INTO orders (id, customer_name, status, total_amount) VALUES
(1, 'Anna', 'pending', 150.00),
(2, 'Mark', 'confirmed', 200.00);

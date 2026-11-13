ALTER TABLE orders ADD COLUMN client_order_id TEXT;
CREATE UNIQUE INDEX idx_orders_client_order_id ON orders(client_order_id) WHERE client_order_id IS NOT NULL;

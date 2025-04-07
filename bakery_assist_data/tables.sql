-- Table: customers (Simulating KNA1 - General Customer Data)
CREATE TABLE customers (
    customer_pk SERIAL PRIMARY KEY, -- Internal Primary Key
    customer_number VARCHAR(10) UNIQUE NOT NULL, -- SAP-like Customer ID (e.g., CUST100001)
    customer_name VARCHAR(255) NOT NULL,
    address_street VARCHAR(255),
    address_city VARCHAR(100),
    address_state VARCHAR(50),
    address_zip VARCHAR(20),
    address_country VARCHAR(50) DEFAULT 'US',
    email VARCHAR(255) UNIQUE,
    phone_number VARCHAR(50),
    customer_group VARCHAR(50), -- e.g., Retail, Wholesale, Cafe
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add index for faster lookups by customer number
CREATE INDEX idx_customer_number ON customers(customer_number);

-- Table: products (Simulating MARA - General Material Data)
CREATE TABLE products (
    product_pk SERIAL PRIMARY KEY, -- Internal Primary Key
    material_number VARCHAR(18) UNIQUE NOT NULL, -- SAP-like Material ID (e.g., MAT-BRD-001)
    product_name VARCHAR(255) NOT NULL,
    product_description TEXT,
    base_unit_of_measure VARCHAR(3) NOT NULL, -- e.g., EA (Each), DZ (Dozen), KG, LB
    product_category VARCHAR(100), -- e.g., Bread, Pastry, Cake, Cookie, Beverage
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add index for faster lookups by material number
CREATE INDEX idx_material_number ON products(material_number);
CREATE INDEX idx_product_category ON products(product_category);


-- Table: invoices (Simulating VBRK - Billing Document Header)
CREATE TABLE invoices (
    invoice_pk SERIAL PRIMARY KEY, -- Internal Primary Key
    invoice_number VARCHAR(20) UNIQUE NOT NULL, -- User-facing Invoice Number (e.g., INV202400001)
    customer_fk INTEGER NOT NULL REFERENCES customers(customer_pk) ON DELETE RESTRICT, -- Link to customer
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    net_amount NUMERIC(12, 2) DEFAULT 0.00, -- Total before tax
    tax_amount NUMERIC(10, 2) DEFAULT 0.00,
    total_amount NUMERIC(12, 2) DEFAULT 0.00, -- Total after tax (net + tax)
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    status VARCHAR(20) NOT NULL DEFAULT 'Open', -- e.g., Open, Paid, Overdue, Cancelled
    payment_terms VARCHAR(50), -- e.g., Net 30, Due on Receipt
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add index for faster lookups by invoice number and customer
CREATE INDEX idx_invoice_number ON invoices(invoice_number);
CREATE INDEX idx_invoice_customer_fk ON invoices(customer_fk);
CREATE INDEX idx_invoice_status ON invoices(status);


-- Table: invoice_items (Simulating VBRP - Billing Document Item)
CREATE TABLE invoice_items (
    invoice_item_pk SERIAL PRIMARY KEY, -- Internal Primary Key
    invoice_fk INTEGER NOT NULL REFERENCES invoices(invoice_pk) ON DELETE CASCADE, -- Link to invoice header
    product_fk INTEGER NOT NULL REFERENCES products(product_pk) ON DELETE RESTRICT, -- Link to product
    item_number INTEGER NOT NULL, -- Line item number (e.g., 10, 20, 30)
    quantity NUMERIC(10, 2) NOT NULL CHECK (quantity > 0), -- Allow fractional quantities (e.g., 1.5 KG)
    unit_of_measure VARCHAR(3) NOT NULL, -- Should ideally match product UOM at time of sale
    unit_price NUMERIC(10, 2) NOT NULL, -- Price at the time of invoicing
    item_total_amount NUMERIC(12, 2) NOT NULL, -- quantity * unit_price
    description TEXT -- Optional: Can store product name or specific notes here
);

-- Add index for faster lookups by invoice and product
CREATE INDEX idx_invoice_item_invoice_fk ON invoice_items(invoice_fk);
CREATE INDEX idx_invoice_item_product_fk ON invoice_items(product_fk);

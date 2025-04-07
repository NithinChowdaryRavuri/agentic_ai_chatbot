import psycopg2
from faker import Faker
import datetime
import random
import decimal # Use Decimal for currency precision

# --- Configuration ---
# Database connection details - MODIFY THESE
DB_HOST = "localhost"
DB_NAME = "bakery_erp_sim" # Use the database name you created
DB_USER = "postgres"       # Your PostgreSQL username
DB_PASSWORD = "1331"       # Your PostgreSQL password

# Data Generation Parameters
NUM_CUSTOMERS = 100
NUM_PRODUCTS = 30
MAX_INVOICES_PER_CUSTOMER = 8
MAX_ITEMS_PER_INVOICE = 6
TAX_RATE = decimal.Decimal('0.08') # Example tax rate (8%)

# --- Realistic Bakery Data ---
BAKERY_PRODUCT_BASES = [
    "Sourdough", "Whole Wheat", "Rye", "Multigrain", "White", "Chocolate",
    "Vanilla", "Red Velvet", "Carrot", "Lemon", "Blueberry", "Strawberry",
    "Apple", "Cheese", "Spinach", "Ham & Cheese", "Almond"
]
BAKERY_PRODUCT_TYPES = {
    "Bread": ["Loaf", "Baguette", "Roll", "Boule"],
    "Pastry": ["Croissant", "Danish", "Muffin", "Scone", "Turnover", "Eclair"],
    "Cake": ["Cake", "Cupcake", "Cheesecake", "Layer Cake", "Bundt Cake"],
    "Cookie": ["Cookie", "Biscotti", "Macaron"],
    "Savory": ["Quiche", "Pie", "Tart", "Focaccia"],
    "Beverage": ["Coffee", "Latte", "Tea", "Juice", "Soda"]
}
UNITS_OF_MEASURE = ["EA", "DZ", "KG", "LB"] # EA=Each, DZ=Dozen
CUSTOMER_GROUPS = ["Retail", "Wholesale", "Cafe", "Online Order", "Event Catering"]
PAYMENT_TERMS = ["Due on Receipt", "Net 15", "Net 30", "Net 60"]
INVOICE_STATUSES = ["Open", "Paid", "Overdue", "Cancelled"]

# Use Decimal for monetary values
decimal.getcontext().prec = 12 # Set precision for Decimal

# Initialize Faker for US locale
fake = Faker('en_US')
# Ensure unique numbers are generated across different calls if needed within a single run
fake.unique.clear()

# --- Database Connection ---
def connect_to_db():
    """Establishes connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("Database connection successful.")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# --- Data Generation Functions ---

def create_fake_customer(conn):
    """Generates and inserts a single fake customer."""
    customer_number = f"CUST{fake.unique.random_number(digits=6, fix_len=True)}"
    # Decide if it's a company or individual (more likely companies for wholesale/cafe)
    customer_name = fake.company() if random.random() > 0.3 else fake.name()
    address_street = fake.street_address()
    address_city = fake.city()
    address_state = fake.state_abbr()
    address_zip = fake.zipcode()
    email = fake.unique.email()
    phone_number = fake.phone_number()
    customer_group = random.choice(CUSTOMER_GROUPS)

    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO customers (customer_number, customer_name, address_street, address_city, address_state, address_zip, email, phone_number, customer_group)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING customer_pk
            """,
            (customer_number, customer_name, address_street, address_city, address_state, address_zip, email, phone_number, customer_group),
        )
        customer_pk = cur.fetchone()[0]
        conn.commit()
        cur.close()
        # print(f"Created Customer: {customer_number} (PK: {customer_pk})")
        return customer_pk
    except psycopg2.Error as e:
        print(f"Error inserting customer {customer_number}: {e}")
        conn.rollback()
        return None

def create_fake_product(conn):
    """Generates and inserts a single fake bakery product."""
    category = random.choice(list(BAKERY_PRODUCT_TYPES.keys()))
    base = random.choice(BAKERY_PRODUCT_BASES)
    type_name = random.choice(BAKERY_PRODUCT_TYPES[category])

    # Construct a more realistic name
    if category == "Beverage":
        product_name = f"{base} {type_name}" if base not in ["Coffee", "Tea", "Juice", "Soda"] else type_name # Avoid "Vanilla Coffee" if type is "Coffee"
    elif category in ["Bread", "Pastry", "Savory"]:
         product_name = f"{base} {type_name}"
    elif category in ["Cake", "Cookie"]:
         product_name = f"{base} {type_name}" # e.g., Chocolate Cake, Vanilla Cupcake
    else:
         product_name = f"{base} {type_name}"

    product_name = product_name.replace("  ", " ").strip() # Clean up potential double spaces

    # Generate a unique material number (simplified SAP-like)
    cat_code = category[:3].upper()
    mat_num = f"MAT-{cat_code}-{fake.unique.random_number(digits=4, fix_len=True)}"

    product_description = fake.sentence(nb_words=10)

    # Assign UOM and Price based on category
    if category == "Bread":
        uom = random.choice(["EA", "KG", "LB"])
        price = decimal.Decimal(random.uniform(3.5, 12.0))
    elif category == "Pastry":
        uom = random.choice(["EA", "DZ"])
        price = decimal.Decimal(random.uniform(1.5, 5.0)) if uom == "EA" else decimal.Decimal(random.uniform(15.0, 45.0))
    elif category == "Cake":
        uom = "EA" # Usually sold as whole items
        price = decimal.Decimal(random.uniform(15.0, 150.0)) # Wider range for cakes
    elif category == "Cookie":
        uom = random.choice(["EA", "DZ", "KG", "LB"])
        price = decimal.Decimal(random.uniform(1.0, 3.5)) if uom == "EA" else decimal.Decimal(random.uniform(10.0, 30.0))
    elif category == "Savory":
        uom = "EA"
        price = decimal.Decimal(random.uniform(4.0, 25.0))
    elif category == "Beverage":
        uom = "EA"
        price = decimal.Decimal(random.uniform(2.0, 6.0))
    else: # Default
        uom = "EA"
        price = decimal.Decimal(random.uniform(1.0, 10.0))

    unit_price = price.quantize(decimal.Decimal("0.01")) # Round to 2 decimal places
    is_active = random.random() > 0.05 # 95% chance of being active

    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO products (material_number, product_name, product_description, base_unit_of_measure, product_category, unit_price, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING product_pk, base_unit_of_measure, unit_price
            """,
            (mat_num, product_name, product_description, uom, category, unit_price, is_active),
        )
        product_pk, base_uom, price = cur.fetchone()
        conn.commit()
        cur.close()
        # print(f"Created Product: {mat_num} - {product_name} (PK: {product_pk})")
        # Return details needed for invoice items
        return {"pk": product_pk, "uom": base_uom, "price": price, "name": product_name}
    except psycopg2.Error as e:
        print(f"Error inserting product {mat_num}: {e}")
        conn.rollback()
        return None

def create_fake_invoice(conn, customer_fk):
    """Generates and inserts a single fake invoice header."""
    invoice_number = f"INV{datetime.date.today().year}{fake.unique.random_number(digits=7, fix_len=True)}"
    invoice_date = fake.date_between(start_date="-2y", end_date="today")
    days_to_due = random.choice([0, 15, 30, 45, 60])
    due_date = invoice_date + datetime.timedelta(days=days_to_due)
    payment_terms = f"Net {days_to_due}" if days_to_due > 0 else "Due on Receipt"
    currency = "USD"
    status = random.choice(INVOICE_STATUSES)
    # Adjust status based on dates for more realism
    if status == "Open" and due_date < datetime.date.today():
        status = "Overdue"
    if status == "Overdue" and invoice_date > datetime.date.today() - datetime.timedelta(days=10): # Less likely recent invoices are overdue
         status = "Open"
    if status == "Paid" and invoice_date > datetime.date.today() - datetime.timedelta(days=5): # Less likely very recent invoices are paid
         status = "Open"


    # Initialize amounts to 0, will be updated after items are added
    net_amount = decimal.Decimal('0.00')
    tax_amount = decimal.Decimal('0.00')
    total_amount = decimal.Decimal('0.00')

    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO invoices (invoice_number, customer_fk, invoice_date, due_date, net_amount, tax_amount, total_amount, currency, status, payment_terms)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING invoice_pk
            """,
            (invoice_number, customer_fk, invoice_date, due_date, net_amount, tax_amount, total_amount, currency, status, payment_terms),
        )
        invoice_pk = cur.fetchone()[0]
        conn.commit()
        cur.close()
        # print(f"Created Invoice Header: {invoice_number} (PK: {invoice_pk})")
        return invoice_pk, invoice_number
    except psycopg2.Error as e:
        print(f"Error inserting invoice {invoice_number}: {e}")
        conn.rollback()
        return None, None

def create_fake_invoice_item(conn, invoice_fk, item_number, product_details):
    """Generates and inserts a single fake invoice item."""
    product_fk = product_details["pk"]
    unit_of_measure = product_details["uom"]
    # Use the price from the product master data (could also add logic for price variations)
    unit_price = product_details["price"]
    description = product_details["name"] # Use product name as description

    # Generate quantity based on UOM
    if unit_of_measure == "DZ":
        quantity = decimal.Decimal(random.randint(1, 10)) # 1 to 10 dozens
    elif unit_of_measure in ["KG", "LB"]:
        quantity = decimal.Decimal(random.uniform(0.5, 5.0)).quantize(decimal.Decimal("0.1")) # 0.5 to 5.0 kg/lb
    else: # "EA"
        quantity = decimal.Decimal(random.randint(1, 50)) # 1 to 50 individual items

    item_total_amount = (quantity * unit_price).quantize(decimal.Decimal("0.01"))

    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO invoice_items (invoice_fk, product_fk, item_number, quantity, unit_of_measure, unit_price, item_total_amount, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (invoice_fk, product_fk, item_number, quantity, unit_of_measure, unit_price, item_total_amount, description),
        )
        # No RETURNING needed here, but we need the item_total_amount for the invoice header update
        conn.commit()
        cur.close()
        # print(f"  - Added Item: {item_number}, Product PK: {product_fk}, Qty: {quantity} {unit_of_measure}, Total: {item_total_amount}")
        return item_total_amount
    except psycopg2.Error as e:
        print(f"Error inserting invoice item for Invoice PK {invoice_fk}, Product PK {product_fk}: {e}")
        conn.rollback()
        return None

def update_invoice_totals(conn, invoice_pk, net_amount):
    """Calculates tax and total amount and updates the invoice header."""
    tax_amount = (net_amount * TAX_RATE).quantize(decimal.Decimal("0.01"))
    total_amount = (net_amount + tax_amount).quantize(decimal.Decimal("0.01"))

    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE invoices
            SET net_amount = %s, tax_amount = %s, total_amount = %s, updated_at = CURRENT_TIMESTAMP
            WHERE invoice_pk = %s
            """,
            (net_amount, tax_amount, total_amount, invoice_pk)
        )
        conn.commit()
        cur.close()
        # print(f"Updated Invoice PK {invoice_pk}: Net={net_amount}, Tax={tax_amount}, Total={total_amount}")
        return total_amount # Return total for final print message
    except psycopg2.Error as e:
        print(f"Error updating invoice totals for Invoice PK {invoice_pk}: {e}")
        conn.rollback()
        return None

# --- Main Execution ---
if __name__ == "__main__":
    start_time = datetime.datetime.now()
    print(f"Starting fake data generation at {start_time}...")

    connection = connect_to_db()
    if connection:
        customer_pks = []
        product_data = [] # Store dicts: {"pk": pk, "uom": uom, "price": price, "name": name}

        print(f"\nGenerating {NUM_CUSTOMERS} customers...")
        for i in range(NUM_CUSTOMERS):
            customer_pk = create_fake_customer(connection)
            if customer_pk:
                customer_pks.append(customer_pk)
            if (i + 1) % 50 == 0: print(f"  ...generated {i+1} customers")


        print(f"\nGenerating {NUM_PRODUCTS} products...")
        for i in range(NUM_PRODUCTS):
            prod_details = create_fake_product(connection)
            if prod_details:
                product_data.append(prod_details)
            if (i + 1) % 10 == 0: print(f"  ...generated {i+1} products")

        if not customer_pks or not product_data:
            print("\nError: No customers or products were generated. Cannot create invoices.")
        else:
            print(f"\nGenerating invoices (max {MAX_INVOICES_PER_CUSTOMER} per customer)...")
            total_invoices_created = 0
            for i, customer_pk in enumerate(customer_pks):
                num_invoices_for_customer = random.randint(1, MAX_INVOICES_PER_CUSTOMER)
                # print(f"  Generating {num_invoices_for_customer} invoices for Customer PK {customer_pk}...")
                for _ in range(num_invoices_for_customer):
                    invoice_pk, invoice_number = create_fake_invoice(connection, customer_pk)
                    if invoice_pk:
                        total_invoices_created += 1
                        invoice_net_amount = decimal.Decimal('0.00')
                        num_items = random.randint(1, MAX_ITEMS_PER_INVOICE)
                        item_number = 10 # Start item numbers at 10, increment by 10 (SAP style)

                        # Ensure we don't add the same product twice to one invoice easily
                        products_in_invoice = set()
                        items_added_count = 0
                        attempts = 0 # Avoid infinite loop if few products exist
                        while items_added_count < num_items and attempts < num_items * 2:
                            attempts += 1
                            selected_product = random.choice(product_data)
                            if selected_product["pk"] not in products_in_invoice:
                                item_total = create_fake_invoice_item(connection, invoice_pk, item_number, selected_product)
                                if item_total is not None:
                                    invoice_net_amount += item_total
                                    item_number += 10
                                    products_in_invoice.add(selected_product["pk"])
                                    items_added_count += 1

                        if invoice_net_amount > 0:
                           final_total = update_invoice_totals(connection, invoice_pk, invoice_net_amount)
                           # Optional: print confirmation for each invoice
                           # if final_total is not None:
                           #     print(f"  --> Created Invoice {invoice_number} (PK: {invoice_pk}) with {items_added_count} items. Total: {final_total} USD")
                        else:
                            # Handle cases where no items were added (e.g., delete the empty invoice header or log)
                            print(f"Warning: Invoice {invoice_number} (PK: {invoice_pk}) created with no items. Net amount is zero.")
                            # Optionally delete it:
                            # cur = connection.cursor()
                            # cur.execute("DELETE FROM invoices WHERE invoice_pk = %s", (invoice_pk,))
                            # connection.commit()
                            # cur.close()

                if (i + 1) % 20 == 0: print(f"  ...processed invoices for {i+1} customers")


        connection.close()
        end_time = datetime.datetime.now()
        print(f"\n--------------------------------------------------")
        print(f"Fake data generation complete at {end_time}.")
        print(f"Duration: {end_time - start_time}")
        print(f"Generated: {len(customer_pks)} Customers, {len(product_data)} Products, {total_invoices_created} Invoices")
        print(f"--------------------------------------------------")

    else:
        print("Failed to connect to the database. Aborting.")
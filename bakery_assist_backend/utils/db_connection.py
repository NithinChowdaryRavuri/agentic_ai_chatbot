import psycopg2

class DataBaseConnection:
    def __init__(self):
        # Database connection details - MODIFY THESE
        self.DB_HOST = "localhost"
        self.DB_NAME = "bakery_erp_sim" # Use the database name you created
        self.DB_USER = "postgres"       # Your PostgreSQL username
        self.DB_PASSWORD = "1331"       # Your PostgreSQL password

    # --- Database Connection Helper ---
    def get_db_connection(self):
        """Establishes and returns a database connection."""
        try:
            conn = psycopg2.connect(
                host=self.DB_HOST,
                database=self.DB_NAME,
                user=self.DB_USER,
                password=self.DB_PASSWORD
            )
            return conn
        except psycopg2.Error as e:
            # Log the error details somewhere accessible to the server admin
            print(f"Database connection error: {e}")
            # In a real app, you might raise a custom exception or handle this differently
            return None
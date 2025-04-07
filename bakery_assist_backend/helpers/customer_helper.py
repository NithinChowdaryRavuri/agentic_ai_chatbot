import psycopg2
from utils.db_connection import DataBaseConnection

class CustomerHelper:
    def __init__(self):
        self.db_connection = DataBaseConnection()

    def get_all_customers(self):
        """
        Fetches all customers from the database.

        Returns:
            list: A list of dictionaries, where each dictionary represents a customer.
            None: If a database error occurs.
        """
        conn = None
        try:
            conn = self.db_connection.get_db_connection()
            if conn is None:
                return None  # Indicate connection failure

            cur = conn.cursor()
            cur.execute("""
                SELECT customer_pk, customer_name, customer_group
                FROM customers
                ORDER BY customer_pk;
            """)
            customers = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            customers_list = [dict(zip(colnames, customer_tuple)) for customer_tuple in customers]
            cur.close()
            return customers_list

        except psycopg2.Error as e:
            print(f"Error fetching customers: {e}")
            return None  # Indicate database error
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
        finally:
            if conn:
                conn.close()

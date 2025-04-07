import psycopg2
from utils.db_connection import DataBaseConnection

class CustomerVerificationHelper:
    def __init__(self):
        self.db_connection = DataBaseConnection()

    def is_valid_customer(self, customer_number):
        """
        Checks if a customer number exists in the database.

        Args:
            customer_number (str): The customer number to verify.

        Returns:
            bool: True if the customer number is valid, False otherwise.
        """
        conn = None
        try:
            conn = self.db_connection.get_db_connection()
            if conn is None:
                return False  # Indicate connection failure

            cur = conn.cursor()
            cur.execute("SELECT 1 FROM customers WHERE customer_pk = %s", (customer_number,))
            exists = cur.fetchone() is not None
            cur.close()
            return exists

        except psycopg2.Error as e:
            print(f"Error verifying customer: {e}")
            return False  # Indicate database error
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False
        finally:
            if conn:
                conn.close()

import json
import psycopg2
from utils.db_connection import DataBaseConnection

class FunctionDeclaration:
    def __init__(self):
       pass

    @staticmethod
    def get_customer_invoices_from_db(customer_number: str, limit: int = 5):
        """
        Retrieves a list of the most recent invoices for a specific customer.
        Args:
            customer_number (str): The unique identifier for the customer (e.g., CUST123456).
            limit (int): The maximum number of invoices to return. Defaults to 5.
        Returns:
            str: A JSON string representing a list of invoices (number, date, total, status)
                or an error message if the customer is not found or an error occurs.
        """
        print(f"--- TOOL CALL: get_customer_invoices_from_db(customer_number={customer_number}, limit={limit}) ---")
        conn = None
        try:
            db_connection = DataBaseConnection()
            conn = db_connection.get_db_connection()
            if conn is None:
                return json.dumps({"error": "Database connection failed"})

            cur = conn.cursor()

            # Fetch invoices
            cur.execute("""
                SELECT invoice_number, invoice_date, total_amount, status
                FROM invoices inv
                JOIN customers cust ON inv.customer_fk = cust.customer_pk
                WHERE cust.customer_pk = %s
                ORDER BY invoice_date DESC
                LIMIT %s
            """, (customer_number, limit))

            invoices = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            invoices_list = []
            for row in invoices:
                # Convert date/decimal directly to string for JSON compatibility
                row_dict = {col: str(val) for col, val in zip(colnames, row)}
                invoices_list.append(row_dict)

            cur.close()
            if not invoices_list:
                return json.dumps({"message": f"No invoices found for customer {customer_number}."})
            return json.dumps(invoices_list) # Return results as a JSON string

        except psycopg2.Error as e:
            print(f"Database error in get_customer_invoices_from_db: {e}")
            return json.dumps({"error": "Database error while fetching invoices."})
        except Exception as e:
            print(f"Unexpected error in get_customer_invoices_from_db: {e}")
            return json.dumps({"error": "An unexpected error occurred."})
        finally:
            if conn:
                conn.close()
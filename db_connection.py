import mysql.connector # type: ignore
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def connect_db():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "cheque_processing")
        )
        if connection.is_connected():
            print("Database connected successfully!")
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
    

def insert_cheque_details(data):
    db = connect_db()
    if db is None:
        return False

    try:
        with db.cursor() as cursor:
            query = '''
                INSERT INTO cheque_details 
                (payee, amount, bank, micr_code, branch, ifsc_code, account_number, cheque_number, date, signature_verification)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            values = (
                data.get("payee", ""),  
                data.get("amount", ""),
                data.get("bank", ""),
                data.get("micr_code", ""),
                data.get("branch", ""),
                data.get("ifsc_code", ""),
                data.get("account_number", ""),
                data.get("cheque_number") if data.get("cheque_number") is not None else None,
                data.get("date", ""),
                data.get("signature_verified") if data.get("signature_verified") is not None else None
            )

            cursor.execute(query, values)
            db.commit()
            print("Cheque details inserted successfully!")
            return True
    except mysql.connector.Error as e:
        print(f"Error inserting data: {e}")
        return False
    finally:
        if db.is_connected():
            db.close()    


def fetch_cheque_details():
    db = connect_db()
    if db is None:
        return None

    try:
        with db.cursor(dictionary=True) as cursor:
            query = "SELECT date, cheque_number, account_number, payee, amount, bank FROM cheque_details"
            cursor.execute(query)
            rows = cursor.fetchall()

        db.close()

        if not rows:
            print("No cheque details found.")
            return None

        return pd.DataFrame(rows)  
    except mysql.connector.Error as e:
        print(f"Database Fetch Error: {e}")
        return None
    finally:
        if db.is_connected():
            db.close()
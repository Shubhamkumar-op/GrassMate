import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    return psycopg.connect(
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT"),
        dbname=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        sslmode="require"
    )


if __name__ == "__main__":

    try:
        with get_connection() as connection:

            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                result = cursor.fetchone()

            print("✅ Connected to Tiger Cloud!")
            print(result[0])

    except Exception as e:
        print("❌ Connection failed.")
        print(e)
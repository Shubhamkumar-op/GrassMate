from src.db.connection import get_connection


def add_trail_metadata():
    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute("""
                ALTER TABLE trails
                ADD COLUMN IF NOT EXISTS activities TEXT,
                ADD COLUMN IF NOT EXISTS interests TEXT,
                ADD COLUMN IF NOT EXISTS features TEXT;
            """)

        connection.commit()

    print("Trail metadata columns added successfully.")


if __name__ == "__main__":
    add_trail_metadata()
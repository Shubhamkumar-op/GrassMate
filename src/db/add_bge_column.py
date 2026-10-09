from src.db.connection import get_connection


def add_bge_column():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                ALTER TABLE chunks
                ADD COLUMN IF NOT EXISTS bge_embedding vector(768);
            """)

        connection.commit()

    print("BGE embedding column added successfully.")


if __name__ == "__main__":
    add_bge_column()
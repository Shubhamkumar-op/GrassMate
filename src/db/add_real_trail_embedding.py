from src.db.connection import get_connection


def add_embedding_column():

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                ALTER TABLE real_trails
                ADD COLUMN IF NOT EXISTS embedding vector(768);
            """)

        connection.commit()

    print("✅ Real trail embedding column added.")


if __name__ == "__main__":
    add_embedding_column()
from src.db.connection import get_connection


def create_schema():
    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute("""
                CREATE EXTENSION IF NOT EXISTS vector;
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS parks (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    location TEXT,
                    description TEXT
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trails (
                    id SERIAL PRIMARY KEY,
                    park_id INTEGER REFERENCES parks(id)
                        ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    distance_km REAL,
                    difficulty TEXT,
                    description TEXT
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    park_id INTEGER REFERENCES parks(id)
                        ON DELETE CASCADE,
                    filename TEXT NOT NULL,
                    content TEXT
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id SERIAL PRIMARY KEY,
                    document_id INTEGER REFERENCES documents(id)
                        ON DELETE CASCADE,
                    chunk_text TEXT NOT NULL,
                    embedding vector(384)
                );
            """)

        connection.commit()

    print("GrassMate database schema created successfully.")


if __name__ == "__main__":
    create_schema()
from src.db.connection import get_connection


def create_trail_search_table():

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trail_search (
                    id SERIAL PRIMARY KEY,

                    trail_name TEXT NOT NULL,

                    latitude DOUBLE PRECISION,

                    longitude DOUBLE PRECISION,

                    distance_km DOUBLE PRECISION,

                    activities TEXT,

                    route_type TEXT,

                    route_category TEXT,

                    retrieval_text TEXT,

                    embedding vector(768),

                    source TEXT DEFAULT 'California State Parks'
                );
            """)

        connection.commit()

    print("✅ trail_search table created.")


if __name__ == "__main__":
    create_trail_search_table()
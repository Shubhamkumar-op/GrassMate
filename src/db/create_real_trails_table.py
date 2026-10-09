from src.db.connection import get_connection


def create_real_trails_table():

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS real_trails (

                    id SERIAL PRIMARY KEY,

                    source_id TEXT UNIQUE,

                    trail_name TEXT NOT NULL,

                    latitude DOUBLE PRECISION,

                    longitude DOUBLE PRECISION,

                    distance_km DOUBLE PRECISION,

                    route_category TEXT,

                    route_type TEXT,

                    activities TEXT,

                    route_description TEXT,

                    trail_description TEXT,

                    source TEXT DEFAULT 'California State Parks'

                );
            """)

        connection.commit()

    print("✅ real_trails table created successfully.")


if __name__ == "__main__":
    create_real_trails_table()
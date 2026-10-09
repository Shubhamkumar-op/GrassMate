from src.db.connection import get_connection


def insert_sample_data():
    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO parks (name, location, description)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (
                    "Central Park",
                    "New York",
                    "A large urban park with walking paths, trees, open spaces, birds, and quiet areas.",
                ),
            )

            park_id = cursor.fetchone()[0]

            trails = [
                (
                    "Lakeside Walking Trail",
                    2.5,
                    "Easy",
                    "A flat trail around the lake with trees, benches, and birdwatching opportunities.",
                ),
                (
                    "Forest Loop",
                    4.0,
                    "Moderate",
                    "A shaded trail through wooded areas with natural scenery and wildlife.",
                ),
                (
                    "Meadow Trail",
                    1.5,
                    "Easy",
                    "A short open trail through a grassy meadow, suitable for a relaxed walk and nature observation.",
                ),
            ]

            for name, distance, difficulty, description in trails:
                cursor.execute(
                    """
                    INSERT INTO trails
                    (park_id, name, distance_km, difficulty, description)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (
                        park_id,
                        name,
                        distance,
                        difficulty,
                        description,
                    ),
                )

        connection.commit()

    print("Sample park and trails inserted successfully.")


if __name__ == "__main__":
    insert_sample_data()
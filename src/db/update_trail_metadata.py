from src.db.connection import get_connection


def update_trail_metadata():
    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute("""
                UPDATE trails
                SET
                    activities = %s,
                    interests = %s,
                    features = %s
                WHERE name = %s;
            """, (
                "walking, birdwatching, nature observation",
                "birds, nature, wildlife, relaxation, photography",
                "lake, trees, benches, water, birds",
                "Lakeside Walking Trail",
            ))

            cursor.execute("""
                UPDATE trails
                SET
                    activities = %s,
                    interests = %s,
                    features = %s
                WHERE name = %s;
            """, (
                "walking, hiking, nature photography, exploration",
                "nature, trees, forest, photography, wildlife, exploration",
                "wooded area, shade, natural scenery, wildlife",
                "Forest Loop",
            ))

            cursor.execute("""
                UPDATE trails
                SET
                    activities = %s,
                    interests = %s,
                    features = %s
                WHERE name = %s;
            """, (
                "walking, photography, sketching, plant observation, relaxation",
                "plants, flowers, nature, photography, art, relaxation",
                "meadow, grass, flowers, open space, plants",
                "Meadow Trail",
            ))

        connection.commit()

    print("Trail metadata updated successfully.")


if __name__ == "__main__":
    update_trail_metadata()
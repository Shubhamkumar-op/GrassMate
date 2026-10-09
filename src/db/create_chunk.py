from src.db.connection import get_connection


def create_chunks():
    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute("""
                DELETE FROM chunks;
            """)

            cursor.execute("""
                DELETE FROM documents;
            """)

            cursor.execute("""
                SELECT
                    t.id,
                    p.id,
                    p.name,
                    p.location,
                    t.name,
                    t.distance_km,
                    t.difficulty,
                    t.activities,
                    t.interests,
                    t.features,
                    t.description
                FROM trails t
                JOIN parks p
                    ON t.park_id = p.id;
            """)

            trails = cursor.fetchall()

            for trail in trails:
                (
                    trail_id,
                    park_id,
                    park_name,
                    location,
                    trail_name,
                    distance_km,
                    difficulty,
                    activities,
                    interests,
                    features,
                    description,
                ) = trail

                chunk_text = f"""
Park: {park_name}
Location: {location}
Trail: {trail_name}
Distance: {distance_km} km
Difficulty: {difficulty}
Activities: {activities}
Interests: {interests}
Features: {features}
Description: {description}
""".strip()

                cursor.execute("""
                    INSERT INTO documents
                    (park_id, filename, content)
                    VALUES (%s, %s, %s)
                    RETURNING id;
                """, (
                    park_id,
                    f"trail_{trail_id}",
                    chunk_text,
                ))

                document_id = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO chunks
                    (document_id, chunk_text)
                    VALUES (%s, %s);
                """, (
                    document_id,
                    chunk_text,
                ))

        connection.commit()

    print("Chunks recreated successfully.")


if __name__ == "__main__":
    create_chunks()
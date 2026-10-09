from src.db.connection import get_connection


def add_more_trails():
    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT id
                FROM parks
                WHERE name = %s;
            """, ("Central Park",))

            park = cursor.fetchone()

            if park is None:
                print("Central Park not found.")
                return

            park_id = park[0]

            trails = [
                (
                    "Garden Discovery Path",
                    1.2,
                    "Easy",
                    "walking, plant observation, photography, exploration",
                    "plants, flowers, gardening, nature, photography",
                    "flower beds, gardens, trees, plants, paths",
                    "A peaceful path through gardens and flowering plants."
                ),
                (
                    "Sunset Ridge",
                    3.0,
                    "Moderate",
                    "walking, hiking, sunset observation, photography",
                    "sunset, landscape, photography, relaxation",
                    "open views, ridge, evening scenery",
                    "A scenic route with open views suitable for watching the sunset."
                ),
                (
                    "Fitness Loop",
                    3.5,
                    "Moderate",
                    "walking, jogging, running, fitness",
                    "fitness, exercise, running, health",
                    "wide paths, open space, loop trail",
                    "A loop suitable for brisk walking, jogging, and outdoor exercise."
                ),
                (
                    "Quiet Reflection Path",
                    1.0,
                    "Easy",
                    "walking, mindfulness, relaxation",
                    "relaxation, mindfulness, peace, stress relief",
                    "quiet path, trees, benches, shade",
                    "A quiet path designed for a peaceful and relaxed outdoor walk."
                ),
                (
                    "Nature Sketch Trail",
                    1.8,
                    "Easy",
                    "walking, sketching, drawing, photography",
                    "art, sketching, drawing, nature, creativity",
                    "trees, plants, flowers, scenic views",
                    "A calm trail with natural scenery suitable for outdoor sketching."
                ),
                (
                    "Forest Explorer Trail",
                    5.0,
                    "Challenging",
                    "hiking, exploration, walking, nature observation",
                    "forest, exploration, adventure, wildlife, nature",
                    "dense trees, forest, natural terrain, wildlife",
                    "A longer trail through wooded areas for outdoor exploration."
                ),
                (
                    "Family Meadow Walk",
                    1.3,
                    "Easy",
                    "walking, family activity, nature observation",
                    "family, children, nature, relaxation",
                    "meadow, open grass, benches, easy paths",
                    "An easy open walk suitable for a relaxed family outing."
                ),
                (
                    "Photography Loop",
                    2.2,
                    "Easy",
                    "walking, photography, exploration",
                    "photography, landscapes, nature, creativity",
                    "scenic views, trees, water, open spaces",
                    "A short loop offering varied natural scenery for photography."
                ),
                (
                    "Cloud Watching Field",
                    0.8,
                    "Easy",
                    "walking, relaxation, observation",
                    "clouds, sky, relaxation, mindfulness",
                    "open field, wide sky, grass",
                    "An open grassy area suitable for relaxing and watching the sky."
                ),
                (
                    "Wildlife Observation Trail",
                    3.8,
                    "Moderate",
                    "walking, wildlife observation, nature observation",
                    "wildlife, animals, nature, observation",
                    "trees, water, natural habitat, wildlife",
                    "A natural trail suitable for observing wildlife from a respectful distance."
                ),
                (
                    "Reading Garden Walk",
                    1.0,
                    "Easy",
                    "walking, reading, relaxation",
                    "reading, books, relaxation, quiet time",
                    "garden, benches, shade, flowers",
                    "A peaceful garden path with quiet places suitable for outdoor reading."
                ),
                (
                    "Social Walking Loop",
                    2.0,
                    "Easy",
                    "walking, social activity, group activity",
                    "friends, socializing, conversation, relaxation",
                    "wide paths, benches, open areas",
                    "An easy loop suitable for walking and talking with friends."
                )
            ]

            for trail in trails:
                cursor.execute("""
                    INSERT INTO trails (
                        park_id,
                        name,
                        distance_km,
                        difficulty,
                        activities,
                        interests,
                        features,
                        description
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """, (
                    park_id,
                    *trail
                ))

        connection.commit()

    print("Additional trails added successfully.")


if __name__ == "__main__":
    add_more_trails()
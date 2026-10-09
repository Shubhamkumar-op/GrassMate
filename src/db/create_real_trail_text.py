from src.db.connection import get_connection


def create_retrieval_text():

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                UPDATE real_trails
                SET retrieval_text =
                    'Trail: ' || COALESCE(trail_name, '') ||
                    E'\\nActivities: ' || COALESCE(activities, '') ||
                    E'\\nSurface: ' || COALESCE(route_type, '') ||
                    E'\\nRoute category: ' || COALESCE(route_category, '') ||
                    E'\\nDistance: ' ||
                        ROUND(COALESCE(distance_km, 0)::numeric, 2) ||
                        ' km' ||
                    E'\\nLocation: latitude ' ||
                        ROUND(COALESCE(latitude, 0)::numeric, 4) ||
                        ', longitude ' ||
                        ROUND(COALESCE(longitude, 0)::numeric, 4)
            """)

        connection.commit()

    print("✅ Retrieval text cleaned.")


if __name__ == "__main__":
    create_retrieval_text()
from src.db.connection import get_connection


def populate_trail_search():

    with get_connection() as connection:

        with connection.cursor() as cursor:

            # Start clean so this script is safe to rerun.
            cursor.execute("""
                DELETE FROM trail_search;
            """)

            cursor.execute("""
                INSERT INTO trail_search (
                    trail_name,
                    latitude,
                    longitude,
                    distance_km,
                    activities,
                    route_type,
                    route_category,
                    retrieval_text
                )

                SELECT DISTINCT ON (
                    LOWER(TRIM(trail_name)),
                    ROUND(latitude::numeric, 2),
                    ROUND(longitude::numeric, 2)
                )

                    trail_name,
                    latitude,
                    longitude,
                    distance_km,
                    activities,
                    route_type,
                    route_category,

                    'Trail: ' || trail_name ||
                    E'\\nActivities: ' || COALESCE(activities, '') ||
                    E'\\nSurface: ' || COALESCE(route_type, '') ||
                    E'\\nRoute category: ' ||
                        COALESCE(route_category, '') ||
                    E'\\nDistance: ' ||
                        ROUND(
                            COALESCE(distance_km, 0)::numeric,
                            2
                        ) ||
                        ' km' ||
                    E'\\nLocation: latitude ' ||
                        ROUND(latitude::numeric, 4) ||
                        ', longitude ' ||
                        ROUND(longitude::numeric, 4)

                FROM real_trails

                WHERE trail_name IS NOT NULL
                  AND TRIM(trail_name) <> ''

                ORDER BY
                    LOWER(TRIM(trail_name)),
                    ROUND(latitude::numeric, 2),
                    ROUND(longitude::numeric, 2),
                    distance_km DESC;
            """)

            cursor.execute("""
                SELECT COUNT(*)
                FROM trail_search;
            """)

            count = cursor.fetchone()[0]

        connection.commit()

    print("✅ trail_search populated.")
    print("Unique retrieval records:", count)


if __name__ == "__main__":
    populate_trail_search()
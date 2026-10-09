from src.db.connection import get_connection


def check_trail_search():

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    id,
                    trail_name,
                    latitude,
                    longitude,
                    distance_km,
                    activities,
                    route_type,
                    route_category,
                    retrieval_text
                FROM trail_search
                ORDER BY id
                LIMIT 10;
            """)

            rows = cursor.fetchall()

    print("\n===== SAMPLE TRAIL SEARCH RECORDS =====")

    for row in rows:

        (
            trail_id,
            trail_name,
            latitude,
            longitude,
            distance_km,
            activities,
            route_type,
            route_category,
            retrieval_text
        ) = row

        print("\n-----------------------------")
        print("ID:", trail_id)
        print("Trail:", trail_name)
        print("Distance:", round(distance_km, 2), "km")
        print("Activities:", activities)
        print("Surface:", route_type)
        print("Category:", route_category)
        print("Location:", latitude, longitude)
        print("\nRetrieval text:")
        print(retrieval_text)


if __name__ == "__main__":
    check_trail_search()
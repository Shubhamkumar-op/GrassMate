from src.db.connection import get_connection


def check_real_trails():

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT COUNT(*)
                FROM real_trails;
            """)

            total = cursor.fetchone()[0]

            print("\n===== REAL TRAIL COUNT =====")
            print("Total:", total)

            cursor.execute("""
                SELECT
                    trail_name,
                    latitude,
                    longitude,
                    distance_km,
                    activities,
                    route_type
                FROM real_trails
                LIMIT 10;
            """)

            rows = cursor.fetchall()

            print("\n===== SAMPLE REAL TRAILS =====")

            for row in rows:
                print("\n-----------------------------")
                print("Trail:", row[0])
                print("Latitude:", row[1])
                print("Longitude:", row[2])
                print("Distance:", row[3], "km")
                print("Activities:", row[4])
                print("Surface:", row[5])


if __name__ == "__main__":
    check_real_trails()
from src.db.connection import get_connection


def check_data():
    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT id, name, location
                FROM parks;
            """)

            parks = cursor.fetchall()

            print("\nPARKS:")
            for park in parks:
                print(park)

            cursor.execute("""
                SELECT name, distance_km, difficulty
                FROM trails;
            """)

            trails = cursor.fetchall()

            print("\nTRAILS:")
            for trail in trails:
                print(trail)


if __name__ == "__main__":
    check_data()
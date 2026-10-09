from src.db.connection import get_connection


def check_retrieval_text():

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    id,
                    trail_name,
                    retrieval_text
                FROM real_trails
                WHERE retrieval_text IS NOT NULL
                LIMIT 3;
            """)

            rows = cursor.fetchall()

    print("\n===== SAMPLE RETRIEVAL DOCUMENTS =====")

    for trail_id, trail_name, text in rows:

        print("\n-----------------------------")
        print("ID:", trail_id)
        print("Trail:", trail_name)
        print("\n" + text)


if __name__ == "__main__":
    check_retrieval_text()
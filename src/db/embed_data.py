from sentence_transformers import SentenceTransformer

from src.db.connection import get_connection


MODEL_NAME = "BAAI/bge-base-en-v1.5"


def generate_embeddings():
    print("Loading BGE embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT id, chunk_text
                FROM chunks
                WHERE bge_embedding IS NULL;
            """)

            chunks = cursor.fetchall()

            print(f"Found {len(chunks)} chunks.")

            for chunk_id, chunk_text in chunks:

                embedding = model.encode(
                    chunk_text,
                    normalize_embeddings=True
                )

                cursor.execute("""
                    UPDATE chunks
                    SET bge_embedding = %s
                    WHERE id = %s;
                """, (
                    embedding.tolist(),
                    chunk_id,
                ))

                print(f"Embedded chunk {chunk_id}")

        connection.commit()

    print("BGE embeddings stored successfully.")


if __name__ == "__main__":
    generate_embeddings()
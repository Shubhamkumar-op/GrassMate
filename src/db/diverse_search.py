
import os
import re
from functools import lru_cache

os.environ["CUDA_VISIBLE_DEVICES"] = ""

from sentence_transformers import SentenceTransformer
from src.db.connection import get_connection


MODEL_NAME = "BAAI/bge-base-en-v1.5"


# --------------------------------------------------
# EMBEDDING MODEL
# --------------------------------------------------

@lru_cache(maxsize=1)
def get_embedding_model():
    """Load the BGE embedding model once and reuse it on CPU."""
    return SentenceTransformer(
        MODEL_NAME,
        device="cpu",
    )


# --------------------------------------------------
# ACTIVITY FILTERING
# --------------------------------------------------

def get_activity_keyword(activity):
    """
    Map user preferences to labels in the current dataset.

    Walking uses hiking-labelled routes as a fallback.
    Exploring and Relaxing do not require a specific activity label.
    Running requires a recorded Run label.
    """

    activity_map = {
        "walking": "hike",
        "hiking": "hike",
        "running": "run",
        "cycling": "bike",
        "exploring": None,
        "relaxing": None,
    }

    if not activity:
        return "hike"

    return activity_map.get(
        activity.strip().lower(),
        "hike",
    )


# --------------------------------------------------
# TRAIL NAME NORMALIZATION
# --------------------------------------------------

def normalize_name(name):
    """Normalize common variations such as Trail and Trl."""
    if not name:
        return ""

    normalized = name.lower().strip()

    normalized = re.sub(
        r"\b(trail|trl)\b",
        "",
        normalized,
    )

    normalized = re.sub(
        r"[^a-z0-9]+",
        " ",
        normalized,
    )

    return " ".join(normalized.split())


# --------------------------------------------------
# DIVERSE TRAIL SEARCH
# --------------------------------------------------

def diverse_search(
    query,
    candidate_limit=50,
    result_limit=5,
    user_latitude=None,
    user_longitude=None,
    radius_km=None,
    activity="Hiking",
):
    """
    Retrieve relevant routes from trail_search using BGE and pgvector.

    Optional geographic filtering uses the Haversine distance formula.

    Each returned record preserves the existing 10-field format:
    0 trail_name
    1 latitude
    2 longitude
    3 recorded segment length
    4 recorded activities
    5 route type
    6 route category
    7 retrieval text
    8 vector distance
    9 distance from search location, or None
    """

    if candidate_limit < 1:
        raise ValueError("candidate_limit must be at least 1.")

    if result_limit < 1:
        raise ValueError("result_limit must be at least 1.")

    use_location = (
        user_latitude is not None
        and user_longitude is not None
        and radius_km is not None
    )

    if use_location:
        if not -90 <= user_latitude <= 90:
            raise ValueError(
                "Latitude must be between -90 and 90."
            )

        if not -180 <= user_longitude <= 180:
            raise ValueError(
                "Longitude must be between -180 and 180."
            )

        if radius_km <= 0:
            raise ValueError(
                "radius_km must be greater than zero."
            )

    # Generate a normalized BGE embedding on CPU.
    model = get_embedding_model()

    query_embedding = model.encode(
        query,
        normalize_embeddings=True,
    ).tolist()

    activity_keyword = get_activity_keyword(activity)

    # Only add a SQL activity filter when a keyword exists.
    activity_condition = ""
    activity_params = []

    if activity_keyword is not None:
        activity_condition = " AND activities ILIKE %s"
        activity_params.append(
            f"%{activity_keyword}%"
        )

    # --------------------------------------------------
    # DATABASE RETRIEVAL
    # --------------------------------------------------

    with get_connection() as connection:
        with connection.cursor() as cursor:

            if use_location:
                sql = f"""
                    WITH nearby_trails AS (
                        SELECT
                            *,
                            6371 * 2 * ASIN(
                                SQRT(
                                    LEAST(
                                        1.0,
                                        GREATEST(
                                            0.0,
                                            POWER(
                                                SIN(
                                                    RADIANS(
                                                        latitude - %s
                                                    ) / 2
                                                ),
                                                2
                                            )
                                            +
                                            COS(RADIANS(%s))
                                            * COS(RADIANS(latitude))
                                            * POWER(
                                                SIN(
                                                    RADIANS(
                                                        longitude - %s
                                                    ) / 2
                                                ),
                                                2
                                            )
                                        )
                                    )
                                )
                            ) AS location_distance_km
                        FROM trail_search
                        WHERE embedding IS NOT NULL
                          AND latitude IS NOT NULL
                          AND longitude IS NOT NULL
                          {activity_condition}
                    )
                    SELECT
                        trail_name,
                        latitude,
                        longitude,
                        distance_km,
                        activities,
                        route_type,
                        route_category,
                        retrieval_text,
                        embedding <=> %s::vector AS vector_distance,
                        location_distance_km
                    FROM nearby_trails
                    WHERE location_distance_km <= %s
                    ORDER BY
                        embedding <=> %s::vector,
                        location_distance_km ASC
                    LIMIT %s;
                """

                # Placeholder order:
                # 1 latitude for distance
                # 2 latitude for cosine
                # 3 longitude for distance
                # 4 optional activity pattern
                # 5 query embedding in SELECT
                # 6 search radius
                # 7 query embedding in ORDER BY
                # 8 candidate limit
                params = [
                    user_latitude,
                    user_latitude,
                    user_longitude,
                    *activity_params,
                    query_embedding,
                    radius_km,
                    query_embedding,
                    candidate_limit,
                ]

            else:
                sql = f"""
                    SELECT
                        trail_name,
                        latitude,
                        longitude,
                        distance_km,
                        activities,
                        route_type,
                        route_category,
                        retrieval_text,
                        embedding <=> %s::vector AS vector_distance,
                        NULL AS location_distance_km
                    FROM trail_search
                    WHERE embedding IS NOT NULL
                      {activity_condition}
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s;
                """

                # IMPORTANT:
                # Placeholder order in this SQL:
                # 1 query embedding in SELECT
                # 2 optional activity pattern in WHERE
                # 3 query embedding in ORDER BY
                # 4 candidate limit
                #
                # When there is no activity filter, parameter 2
                # is absent from the SQL and its parameter list.
                params = [
                    query_embedding,
                    *activity_params,
                    query_embedding,
                    candidate_limit,
                ]

            cursor.execute(sql, params)
            candidates = cursor.fetchall()

    # --------------------------------------------------
    # QUALITY FILTERING AND DEDUPLICATION
    # --------------------------------------------------

    selected = []
    seen_routes = set()

    for trail in candidates:
        (
            trail_name,
            latitude,
            longitude,
            distance_km,
            activities,
            route_type,
            route_category,
            retrieval_text,
            vector_distance,
            location_distance_km,
        ) = trail

        if not trail_name or not trail_name.strip():
            continue

        if trail_name.lower().strip() in {
            "unknown",
            "unnamed",
            "unamed",
        }:
            continue

        # Exclude missing and very short recorded segments.
        if distance_km is None or distance_km < 0.10:
            continue

        if not activities:
            continue

        # Validate activity labels when a specific label is required.
        if (
            activity_keyword is not None
            and activity_keyword not in activities.lower()
        ):
            continue

        normalized = normalize_name(trail_name)

        if not normalized:
            continue

        # Use approximate location as part of the key so trails
        # with the same name in different places can remain distinct.
        if latitude is not None and longitude is not None:
            route_key = (
                normalized,
                round(latitude, 3),
                round(longitude, 3),
            )
        else:
            route_key = (
                normalized,
                None,
                None,
            )

        if route_key in seen_routes:
            continue

        seen_routes.add(route_key)
        selected.append(trail)

        if len(selected) >= result_limit:
            break

    return selected


# --------------------------------------------------
# TEST ALL SIX ACTIVITIES
# --------------------------------------------------

if __name__ == "__main__":

    test_activities = [
        "Walking",
        "Running",
        "Hiking",
        "Cycling",
        "Exploring",
        "Relaxing",
    ]

    for requested_activity in test_activities:

        query = (
            f"I want an outdoor route for "
            f"{requested_activity.lower()} and enjoying nature."
        )

        print("\n" + "=" * 55)
        print(f"Requested activity: {requested_activity}")
        print("=" * 55)

        try:
            results = diverse_search(
                query=query,
                candidate_limit=50,
                result_limit=5,
                activity=requested_activity,
            )

            if not results:
                print(
                    "No matching routes found in the current "
                    "indexed dataset."
                )
                continue

            for index, trail in enumerate(results, start=1):

                (
                    name,
                    latitude,
                    longitude,
                    segment_length,
                    activities,
                    route_type,
                    route_category,
                    retrieval_text,
                    vector_distance,
                    location_distance,
                ) = trail

                print(f"\n{index}. {name}")
                print(f"   Recorded activities: {activities}")

                print(
                    f"   Recorded segment: "
                    f"{segment_length:.2f} km"
                )

                print(f"   Route type: {route_type}")
                print(f"   Route category: {route_category}")

                if vector_distance is not None:
                    print(
                        f"   Vector distance: "
                        f"{vector_distance:.4f}"
                    )

                if location_distance is not None:
                    print(
                        f"   Distance from search location: "
                        f"{location_distance:.2f} km"
                    )

        except Exception as exc:
            print(f"Search failed: {exc}")

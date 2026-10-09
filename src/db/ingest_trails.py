import geopandas as gpd

from src.db.connection import get_connection


FILE_PATH = "data/recreational_routes/RecreationalRoutes.shp"


def load_trails():

    print("Loading California State Parks dataset...")

    routes = gpd.read_file(FILE_PATH)

    print(f"Raw routes: {len(routes)}")

    # Keep State Park Trail routes that support hiking.
    trails = routes[
        (
            routes["ROUTECLASS"]
            .fillna("")
            .str.strip()
            .str.lower()
            == "state park trail"
        )
        &
        (
            routes["TRAILDES"]
            .fillna("")
            .str.contains(
                "Hike",
                case=False,
                regex=False
            )
        )
    ].copy()

    print(f"Hiking trail segments: {len(trails)}")

    # Remove unnamed routes.
    trails = trails[
        ~trails["ROUTENAME"]
        .fillna("")
        .str.strip()
        .str.lower()
        .isin(["unnamed", "unamed"])
    ].copy()

    print(f"After removing unnamed routes: {len(trails)}")

    # Remove empty/invalid geometry.
    trails = trails[
        trails.geometry.notna()
        & ~trails.geometry.is_empty
    ].copy()

    print(f"After removing invalid geometry: {len(trails)}")

    # Transform to a California metric CRS.
    trails = trails.to_crs("EPSG:3310")

    # Calculate geometry length in kilometers.
    trails["distance_km"] = (
        trails.geometry.length / 1000
    )

    # Get representative point for each route segment.
    points = trails.geometry.representative_point()

    # Transform points to latitude/longitude.
    points = points.to_crs("EPSG:4326")

    trails["longitude"] = points.x
    trails["latitude"] = points.y

    print("\nConnecting to Tiger Data...")

    with get_connection() as connection:

        with connection.cursor() as cursor:

            inserted = 0

            for _, row in trails.iterrows():

                source_id = str(row["GISID"])

                trail_name = str(row["ROUTENAME"]).strip()

                activities = str(
                    row["TRAILDES"]
                ).strip()

                route_category = str(
                    row["ROUTECAT"]
                ).strip()

                route_type = str(
                    row["ROUTETYPE"]
                ).strip()

                route_description = str(
                    row["ROUTEDES"]
                ).strip()

                trail_description = str(
                    row["TRAILDES"]
                ).strip()

                cursor.execute(
                    """
                    INSERT INTO real_trails (
                        source_id,
                        trail_name,
                        latitude,
                        longitude,
                        distance_km,
                        route_category,
                        route_type,
                        activities,
                        route_description,
                        trail_description
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (source_id)
                    DO NOTHING;
                    """,
                    (
                        source_id,
                        trail_name,
                        row["latitude"],
                        row["longitude"],
                        row["distance_km"],
                        route_category,
                        route_type,
                        activities,
                        route_description,
                        trail_description
                    )
                )

                if cursor.rowcount == 1:
                    inserted += 1

        connection.commit()

    print("\n===== INGESTION COMPLETE =====")
    print(f"Inserted: {inserted}")
    print(f"Processed: {len(trails)}")


if __name__ == "__main__":
    load_trails()
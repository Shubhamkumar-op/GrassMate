import geopandas as gpd

FILE_PATH = "data/recreational_routes/RecreationalRoutes.shp"

routes = gpd.read_file(FILE_PATH)

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

print("\n===== ROUTE CATEGORY + ACTIVITY =====")

print(
    trails.groupby(
        ["ROUTECAT", "TRAILDES"]
    ).size()
    .sort_values(ascending=False)
    .to_string()
)

print("\n===== ROUTE CATEGORY COUNTS =====")

print(
    trails["ROUTECAT"]
    .value_counts(dropna=False)
    .to_string()
)
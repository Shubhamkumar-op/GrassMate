import geopandas as gpd

FILE_PATH = "data/recreational_routes/RecreationalRoutes.shp"

routes = gpd.read_file(FILE_PATH)

print("\n===== DATASET INFO =====")
print("Number of routes:", len(routes))

print("\n===== COLUMNS =====")
for column in routes.columns:
    print(column)

print("\n===== FIRST 5 ROUTES =====")
print(routes.head().to_string())

print("\n===== DATA TYPES =====")
print(routes.dtypes)

print("\n===== CRS =====")
print(routes.crs)
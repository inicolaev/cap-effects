import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely import wkt
import matplotlib.pyplot as plt

def plot_unsold_cap(gdf, cap_value, vmin, vmax):
    column_name = f"unsold_cap_{cap_value}"
    # Check if the column exists
    if column_name not in gdf.columns:
        st.error(f"Column {column_name} does not exist in the dataframe.")
        return
    # Plotting the map with fixed vmin and vmax
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.plot(column=column_name, legend=True, cmap='OrRd', vmin=vmin, vmax=vmax, ax=ax)
    plt.title(f"Unsold Cap {cap_value} Visualization")
    st.pyplot(fig)

# Load the data
file_path = 'cap_effects.csv'
df = pd.read_csv(file_path)

# Convert the WKT geometry to a GeoSeries
df['geometry'] = df['geometry'].apply(wkt.loads)

# Convert DataFrame to GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry='geometry')

# Ensure the GeoDataFrame has a proper coordinate reference system (CRS)
# This will depend on your data. If it's not provided, you may need to set it.
gdf.set_crs(epsg=4326, inplace=True)  # Example CRS, adjust if necessary

# Calculate the global min and max across the `unsold_cap_*` columns
min_value = gdf[[f'unsold_cap_{i}' for i in range(10, 14)]].min().min()
max_value = gdf[[f'unsold_cap_{i}' for i in range(10, 14)]].max().max()

# Streamlit app
st.title("Canadian Tier 4 Service Areas Cap Visualization")

# Sidebar for user input
cap_value = st.sidebar.slider("Select Cap Value", min_value=10, max_value=13, value=10)

# Plot the map with consistent legend scaling
plot_unsold_cap(gdf, cap_value, vmin=min_value, vmax=max_value)

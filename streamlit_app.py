import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely import wkt
import folium
from streamlit_folium import folium_static

def plot_unsold_cap_interactive(gdf, cap_value):
    column_name = f"unsold_cap_{cap_value}"
    # Check if the column exists
    if column_name not in gdf.columns:
        st.error(f"Column {column_name} does not exist in the dataframe.")
        return

    # Make sure the column is in the correct data type
    gdf[column_name] = gdf[column_name].astype(float)
    
    # Retrieve previous map center and zoom if it exists
    if "last_center" in st.session_state and "last_zoom" in st.session_state:
        last_center = st.session_state["last_center"]
        last_zoom = st.session_state["last_zoom"]
    else:
        last_center = [56.1304, -106.3468]
        last_zoom = 4
    
    # Initialize the map with the previous or default center/zoom
    m = folium.Map(location=last_center, zoom_start=last_zoom)
    
    # Define bins for the legend
    bins = list(range(15))  # Creates bins from 0 to 14

    # Create a choropleth map
    choropleth = folium.Choropleth(
        geo_data=gdf,
        name="choropleth",
        data=gdf,
        columns=["Service Area #", column_name],
        key_on="feature.properties.Service Area #",
        fill_color="OrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Number of unsold blocks",
        bins=bins,
        highlight=True,
        nan_fill_color="white",
        nan_fill_opacity=0.7,
        reset=True,
    ).add_to(m)
    
    # Add tooltips to each service area
    for _, row in gdf.iterrows():
        tooltip = folium.Tooltip(f"Service Area: {row['Service Area #']}<br>Unsold Blocks: {row[column_name]}")
        folium.GeoJson(
            row['geometry'],
            tooltip=tooltip,
            style_function=lambda x: {'fillColor': '#ffffff00', 'weight': 0}
        ).add_to(m)

    folium.LayerControl().add_to(m)

    # Add script to save map center and zoom level on change
    save_center_zoom_js = """
    function save_center_zoom() {
        var map_center = [map.getCenter().lat, map.getCenter().lng];
        var map_zoom = map.getZoom();
        document.getElementById('last_center').value = map_center;
        document.getElementById('last_zoom').value = map_zoom;
    }
    map.on('moveend', save_center_zoom);
    map.on('zoomend', save_center_zoom);
    """
    m.get_root().html.add_child(folium.Element("""
        <input type="hidden" id="last_center" name="last_center" value="{}">
        <input type="hidden" id="last_zoom" name="last_zoom" value="{}">
    """.format(last_center, last_zoom)))
    m.get_root().script.add_child(folium.Element(save_center_zoom_js))

    # Streamlit custom event to read hidden inputs and save state
    folium_static(m)
    st.session_state["last_center"] = eval(st.experimental_get_query_params().get('last_center', '[]')[0])
    st.session_state["last_zoom"] = int(st.experimental_get_query_params().get('last_zoom', [last_zoom])[0])

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
st.title("Impact of Spectrum Cap on the 3800 MHz and Residual Auction")

# Sidebar for user input
cap_value = st.sidebar.slider("Select Cap Value", min_value=10, max_value=13, value=10)

# Plot the interactive map
plot_unsold_cap_interactive(gdf, cap_value)

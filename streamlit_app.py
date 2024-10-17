import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely import wkt
import folium
from streamlit_folium import folium_static
import numpy as np

@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df['geometry'] = df['geometry'].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry='geometry')
    gdf.set_crs(epsg=4326, inplace=True)
    return gdf

@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

def plot_unsold_cap_interactive(gdf, cap_value):
    column_name = f"unsold_cap_{cap_value}"
    if column_name not in gdf.columns:
        st.error(f"Column {column_name} does not exist in the dataframe.")
        return
    
    gdf[column_name] = gdf[column_name].astype(float)
    gdf = gdf.dropna(subset=[column_name])
    
    min_value = gdf[column_name].min()
    max_value = gdf[column_name].max()
    
    # Create at least 4 bins
    if min_value == max_value:
        bins = [min_value - 1, min_value, min_value + 1, min_value + 2]
    else:
        bins = np.linspace(min_value, max_value, num=5)
    bins = sorted(list(set([float(round(b, 2)) for b in bins])))
    
    if "map_center" not in st.session_state:
        st.session_state["map_center"] = [56.1304, -106.3468]
    if "map_zoom" not in st.session_state:
        st.session_state["map_zoom"] = 4
    
    m = folium.Map(location=st.session_state["map_center"], zoom_start=st.session_state["map_zoom"])
    
    choropleth = folium.Choropleth(
        geo_data=gdf,
        name="choropleth",
        data=gdf,
        columns=["Service Area #", column_name],
        key_on="feature.properties.Service Area #",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Number of unsold blocks",
        bins=bins,
        highlight=True,
        nan_fill_color="white",
        nan_fill_opacity=0.7,
        reset=True,
    ).add_to(m)
    
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(['Service Area #', column_name], labels=False)
    )
    
    # Add tooltips to each service area
    for _, row in gdf.iterrows():
        tooltip = folium.Tooltip(
            f"Service Area: {row['Service Area #']}<br>"
            f"Unsold Blocks: {row[column_name]:.2f}<br>"
            f"Total Blocks: {row['total_blocks']}"  # Assuming you have this column
        )
        folium.GeoJson(
            row['geometry'],
            tooltip=tooltip,
            style_function=lambda x: {'fillColor': '#ffffff00', 'weight': 0}
        ).add_to(m)

    folium.LayerControl().add_to(m)

    # Add a custom script to store the map's center and zoom in the session state
    save_center_zoom_js = """
    function saveMapCenterZoom(map) {
        var map_center = map.getCenter();
        var map_zoom = map.getZoom();
        sessionStorage.setItem('map_center', JSON.stringify(map_center));
        sessionStorage.setItem('map_zoom', map_zoom);
    }
    map.on('moveend', function() { saveMapCenterZoom(map); });
    map.on('zoomend', function() { saveMapCenterZoom(map); });
    """
    m.get_root().script.add_child(folium.Element(save_center_zoom_js))

    folium_static(m)
    
    if st.experimental_get_query_params().get('map_center') and st.experimental_get_query_params().get('map_zoom'):
        st.session_state["map_center"] = eval(st.experimental_get_query_params().get('map_center')[0])
        st.session_state["map_zoom"] = int(st.experimental_get_query_params().get('map_zoom')[0])

# Streamlit app
st.title("Impact of Spectrum Cap on the 3800 MHz and Residual Auction")

# Load the dataset
file_path = 'cap_effects.csv'  # Adjust this to the correct file path
gdf = load_data(file_path)

# Dynamically calculate the available unsold_cap_* columns in the dataset
available_cap_columns = [col for col in gdf.columns if col.startswith('unsold_cap_')]
min_cap_value = int(available_cap_columns[0].split('_')[-1])
max_cap_value = int(available_cap_columns[-1].split('_')[-1])

# Sidebar for user input with dynamic cap range
cap_value = st.sidebar.slider("Select Cap Value", min_value=min_cap_value, max_value=max_cap_value, value=min_cap_value)

# Display summary statistics
column_name = f"unsold_cap_{cap_value}"
st.sidebar.write(f"Total unsold blocks: {gdf[column_name].sum():.2f}")
st.sidebar.write(f"Average unsold blocks per area: {gdf[column_name].mean():.2f}")

# Add a download button for the data
csv = convert_df(gdf[['Service Area #', column_name]])
st.sidebar.download_button(
    "Download data as CSV",
    csv,
    f"unsold_blocks_cap_{cap_value}.csv",
    "text/csv",
    key='download-csv'
)

# Add a title and description to the map
st.write(f"Map showing unsold spectrum blocks with a cap of {cap_value} MHz")
st.write("The color intensity indicates the number of unsold blocks in each service area.")

# Plot the interactive map
plot_unsold_cap_interactive(gdf, cap_value)

# Add a comparison feature
st.write("Compare two cap values:")
col1, col2 = st.columns(2)
with col1:
    cap_value1 = st.slider("Select Cap Value 1", min_value=min_cap_value, max_value=max_cap_value, value=min_cap_value, key="cap1")
    plot_unsold_cap_interactive(gdf, cap_value1)
with col2:
    cap_value2 = st.slider("Select Cap Value 2", min_value=min_cap_value, max_value=max_cap_value, value=max_cap_value, key="cap2")
    plot_unsold_cap_interactive(gdf, cap_value2)

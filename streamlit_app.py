import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely import wkt
import folium
from streamlit_folium import folium_static
import numpy as np
import branca.colormap as cm
from streamlit.config import get_option

# Set the page to wide mode
st.set_page_config(layout="wide")

def plot_unsold_cap_interactive(gdf, cap_value):
    column_name = f"unsold_cap_{cap_value}"
    if column_name not in gdf.columns:
        st.error(f"Column {column_name} does not exist in the dataframe.")
        return
    
    gdf[column_name] = gdf[column_name].astype(float)
    gdf = gdf.dropna(subset=[column_name])
    
    min_value = gdf[column_name].min()
    max_value = gdf[column_name].max()
    
    if "map_center" not in st.session_state:
        st.session_state["map_center"] = [56.1304, -106.3468]
    if "map_zoom" not in st.session_state:
        st.session_state["map_zoom"] = 4
    
    m = folium.Map(location=st.session_state["map_center"], zoom_start=st.session_state["map_zoom"])
    
    # Create a custom colormap for values > 1
    colormap = cm.LinearColormap(
        colors=['#FFA500', '#FF0000'],
        vmin=1,
        vmax=max_value
    )
    
    # Custom color function
    def get_color(value):
        if value == 0:
            return '#00FF00'  # Green
        elif value == 1:
            return '#FFFF00'  # Yellow
        else:
            return colormap(value)

    # Add GeoJson layer with custom style
    folium.GeoJson(
        gdf,
        style_function=lambda feature: {
            'fillColor': get_color(feature['properties'][column_name]),
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['Service Area #', column_name],
            aliases=['Service Area:', 'Unsold Blocks:'],
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: #F0EFEF;
                border: 2px solid black;
                border-radius: 3px;
                box-shadow: 3px;
            """,
            max_width=800,
        ),
    ).add_to(m)

    # Create a custom color legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; width: 220px; height: 120px; 
                border:2px solid grey; z-index:9999; font-size:14px; background-color:white;
                ">&nbsp; <b>Number of unsold blocks</b> <br>
    &nbsp; <i class="fa fa-square" style="color:#00FF00;"></i> 0 <br>
    &nbsp; <i class="fa fa-square" style="color:#FFFF00;"></i> 1 <br>
    &nbsp; <i class="fa fa-square" style="color:#FFA500;"></i> 2 <br>
    &nbsp; <i class="fa fa-square" style="color:#FF0000;"></i> {:.0f}+ <br>
    </div>
    '''.format(max_value)
    m.get_root().html.add_child(folium.Element(legend_html))

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

    # Set fixed width and height for the map
    width = 1300
    height = 800

    # Display the map with custom width and height
    folium_static(m, width=width, height=height)
    
    if st.experimental_get_query_params().get('map_center') and st.experimental_get_query_params().get('map_zoom'):
        st.session_state["map_center"] = eval(st.experimental_get_query_params().get('map_center')[0])
        st.session_state["map_zoom"] = int(st.experimental_get_query_params().get('map_zoom')[0])

    # Calculate and display the sum of unsold blocks
    sum_unsold_blocks = gdf[column_name].sum()
    st.write(f"Sum of unsold blocks for cap of {cap_value} blocks: {int(sum_unsold_blocks)}")


# Load the new dataset
file_path = 'cap_effects.csv'  # Adjust this to the correct file path
df = pd.read_csv(file_path)

# Convert the WKT geometry to a GeoSeries
df['geometry'] = df['geometry'].apply(wkt.loads)

# Convert DataFrame to GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry='geometry')

# Ensure the GeoDataFrame has a proper coordinate reference system (CRS)
gdf.set_crs(epsg=4326, inplace=True)

# Dynamically calculate the available unsold_cap_* columns in the dataset
available_cap_columns = [col for col in gdf.columns if col.startswith('unsold_cap_')]
min_cap_value = int(available_cap_columns[0].split('_')[-1])
max_cap_value = int(available_cap_columns[-1].split('_')[-1])

# Streamlit app
st.title("Impact of Spectrum Cap on the 3800 MHz and Residual Auction")

# Sidebar for user input with dynamic cap range
cap_value = st.sidebar.slider("Select Cap Value", min_value=min_cap_value, max_value=max_cap_value, value=min_cap_value)

# Plot the interactive map
plot_unsold_cap_interactive(gdf, cap_value)

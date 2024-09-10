import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely import wkt
import matplotlib.pyplot as plt

# Store the correct username and password as a dictionary
users = {
    "admin": "pass123" 
}

def check_password(username, password):
    """Checks if the provided username and password match the stored credentials."""
    if username in users and users[username] == password:
        return True
    return False

def login_form():
    """Renders a login form within the app."""
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button("Login")

    if login_button:
        if check_password(username, password):
            st.session_state["authenticated"] = True
            st.sidebar.success("Logged in as {}".format(username))
        else:
            st.sidebar.error("Incorrect username or password")

def logout_button():
    """Renders a logout button in the sidebar."""
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.sidebar.success("Successfully logged out")

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

# Initialize 'authenticated' in session state if not already present
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

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

if not st.session_state["authenticated"]:
    login_form()
else:
    # Add a logout button
    logout_button()

    # User is authenticated, display the main content
    st.title("Canadian Tier 4 Service Areas Cap Visualization")

    # Sidebar for user input
    cap_value = st.sidebar.slider("Select Cap Value", min_value=10, max_value=13, value=10)

    # Plot the map with consistent legend scaling
    plot_unsold_cap(gdf, cap_value, vmin=min_value, vmax=max_value)

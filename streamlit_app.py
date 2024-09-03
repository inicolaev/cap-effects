import streamlit as st

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

# Initialize 'authenticated' in session state if not already present
if "authenticated" not in st.session_state:
  st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
  login_form()
else:
  # User is authenticated, display the main content
  st.title("My Streamlit App")
  x = st.slider("Select a value")
  st.write(x, "squared is", x * x)

import streamlit as st
import streamlit_authenticator as stauth

# Define your users, usernames, and passwords
names = ["John Doe", "Jane Doe"]
usernames = ["johndoe", "janedoe"]
passwords = ["password1", "password2"]

# Hash the passwords
hashed_passwords = stauth.Hasher(passwords).generate()

# Create the authenticator object
authenticator = stauth.Authenticate(
    credentials={"usernames": 
                    {"johndoe": {"name": "John Doe", "password": hashed_passwords[0]},
                     "janedoe": {"name": "Jane Doe", "password": hashed_passwords[1]}
                    }
                 },
    cookie_name="some_cookie_name",
    key="some_signature_key",
    cookie_expiry_days=30
)

# Login process
name, authentication_status, username = authenticator.login("Login", "main")

# If login is successful
if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.write(f'Welcome *{name}*')
    st.write("This is the main content of the dashboard.")
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')

x = st.slider("Select a value")
st.write(x, "squared is", x * x)

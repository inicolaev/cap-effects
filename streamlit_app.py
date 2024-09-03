import streamlit as st
import streamlit_authenticator as stauth

# Define your users and passwords
names = ["John Doe", "Jane Doe"]
usernames = ["johndoe", "janedoe"]
passwords = ["123", "456"]

# Hash the passwords
hashed_passwords = stauth.Hasher(passwords).generate()

# Create authenticator
authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "some_cookie_name", "some_signature_key", cookie_expiry_days=30)

# Login
name, authentication_status, username = authenticator.login("Login", "main")

# If login is successful
if authentication_status:
    st.write(f'Welcome *{name}*')
    st.write("Add your Streamlit dashboard code here")
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')

x = st.slider("Select a value")
st.write(x, "squared is", x * x)

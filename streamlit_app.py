import streamlit as st
import streamlit_authenticator as stauth

# User credentials
names = ["John Doe", "Jane Doe"]
usernames = ["johndoe", "janedoe"]
passwords = ["password1", "password2"]

# Hash passwords
hashed_passwords = stauth.Hasher(passwords).generate()

# Create the authenticator object
authenticator = stauth.Authenticate(names=names, usernames=usernames, passwords=hashed_passwords, 
                                    cookie_name="some_cookie_name", cookie_key="some_signature_key",
                                    cookie_expiry_days=30)

# Login process
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.write(f'Welcome *{name}*')
    st.write("Add your Streamlit dashboard code here")
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')

x = st.slider("Select a value")
st.write(x, "squared is", x * x)

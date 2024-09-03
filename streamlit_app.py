import streamlit as st
import streamlit_authenticator as stauth

names = ["admin", "guest"]
usernames = ["admin", "guest"]
passwords = ["123", "456"]

hashed_passwords = stauth.hasher(passwords).generate()
authenticator = stauth.authenticate(names, usernames, hashed_passwords, "some_cookie_name", "some_signature_key", cookie_expiry_days=30)

name, authentication_status = authenticator.login("Login", "main")

if authentication_status:
    st.write(f'Welcome *{name}*')
    st.write("Add your Streamlit dashboard code here")
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')

x = st.slider("Select a value")
st.write(x, "squared is", x * x)

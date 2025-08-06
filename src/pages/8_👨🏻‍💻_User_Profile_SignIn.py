import pandas as pd
import streamlit as st

from utils.db import DataBaseManagement
from utils.decandenc import encrypt, generate_key

"""
A Streamlit-based User Profile Management page.

Features:
- Allows users to create or update their profile by entering details such as name, title, profession, signature, email, and password.
- Encrypts the user's password securely before storing it in the database.
- Saves the logged-in user’s email and login status in the Streamlit session state after successful profile creation.
- Retrieves and displays all stored user profiles from the database in a formatted table.
- Masks passwords when displaying user profiles for security purposes.
- Provides error messages when required fields are missing or if profile creation fails.
"""


st.title("User Profile")
st.subheader("Please enter your profile details")

name = st.text_input("Full Name", placeholder="Enter your full name")
title = st.text_input("Title", placeholder="Enter your title (e.g., Mr., Mrs.)")
proffesion = st.text_input("Profession", placeholder="Enter your profession")
signiture = st.text_input("Signature", placeholder="Enter your signature (optional)")
email = st.text_input("Email", placeholder="Enter your email address")
password = st.text_input("Password", type="password", placeholder="Enter a secure password")

if st.button("Submit Profile"):
    if name and title and proffesion and signiture and email and password:
        db = DataBaseManagement()
        # Decrypt the password before send it to datbase
        encrypted_password = encrypt(password, generate_key("securepassword"))
        # set user profile in dateabse
        result = db.set_user_profile(name, title, proffesion, signiture, email, encrypted_password)
        if result:
            st.success("Profile created successfully!")
            st.session_state.user_email = email  # save email in st.session
            st.session_state.logged_in = True  # change logged in status
        else:
            st.error("Failed to create profile. Please try again.")
    else:
        st.error("Please fill in all fields.")

# Show user profile
db = DataBaseManagement()
user_profiles = db.get_all_user_profile()

if user_profiles:
    user_data = {
        "User_id": [user[0] for user in user_profiles],
        "Name": [user[1] for user in user_profiles],  # indx 1 for name
        "Title": [user[2] for user in user_profiles],  # indx 2 for title
        "Profession": [user[3] for user in user_profiles],  # indx 3 for profession
        "Signature": [user[4] for user in user_profiles],  # indx 4 for signature
        "Email": [user[5] for user in user_profiles],  #indx 5 for email
        "Password": ["*" * len(user[6]) for user in user_profiles], # indx 6 for password
    }
    dataframe = pd.DataFrame(user_data)
    dataframe = dataframe.set_index("User_id")

    # show dataframe
    st.write("User Profile Information:")
    st.dataframe(dataframe)

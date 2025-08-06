import pandas as pd
import streamlit as st

from utils.db import DataBaseManagement

st.set_page_config(page_title="Profiles", page_icon=":zap:")

def profile_page():
    # Make sure user is logged in...
    if "user_email" in st.session_state and "user_id" in st.session_state:
        user_id = st.session_state.user_id
        user_email = st.session_state.user_email
        if user_authentication(user_id, user_email):
            db = DataBaseManagement()
            user_profile = db.get_user_profile(user_id=user_id, email=user_email)

            if not user_profile:
                st.error("User profile not found!")
                return

            user_name = user_profile[1]
            user_title = user_profile[2]
            st.title(f"{user_title} {user_name} Please Add Profiles")
            st.markdown("##### Add people you want to send emails to 📨 ")
            st.write("---" * 100)

            # profile form to submit profiles
            with st.form(key="profile_form"):
                col1, col2 = st.columns([2, 2])
                with col1:
                    name = st.text_input("Full Name", placeholder="Enter profile's full name")
                    title = st.text_input("Title", placeholder="Enter profile title (Mr., Mrs., etc.)")
                with col2:
                    email = st.text_input("Email", placeholder="Enter profile email (profile@example.com)")
                    profession = st.text_input("Profession", placeholder="Enter profile profession (e.g., programmer, doctor)")

                submit_button = st.form_submit_button(label="Submit")
                if submit_button:
                    if name and title and email and profession:
                        results = db.add_profile(name=name, email=email, title=title, proffesion=profession, user_id=user_id)
                        if results:
                            st.success("✅ Profile added successfully!")
                        else:
                            st.error("❌ Failed to add profile")
                    else:
                        st.error("❌ Please fill in all fields")

            # Show all profiles
            if st.button("Show all profiles 🧐"):
                profiles = db.get_all_profiles(user_id)
                if profiles:
                    profile_data = {
                        "Id": [prof[0] for prof in profiles],
                        "Name": [prof[1] for prof in profiles],
                        "Title": [prof[3] for prof in profiles],
                        "Email": [prof[2] for prof in profiles],
                        "Profession": [prof[4] for prof in profiles],
                    }
                    dataframe = pd.DataFrame(profile_data).set_index("Id")
                    st.dataframe(dataframe)
                else:
                    st.info("No profiles found for this user.")

            # search in profiles
            st.write("---" * 100)
            st.markdown("### Looking for specific profile?")
            search_email = st.text_input("Search by email", placeholder="Enter profile's email")
            if st.button("Search") and search_email:
                searched_profile = db.get_profile(email=search_email, user_id=user_id)
                if searched_profile:
                    dataframe = pd.DataFrame([{
                        "Id": searched_profile[0],
                        "Name": searched_profile[1],
                        "Title": searched_profile[3],
                        "Email": searched_profile[2],
                        "Profession": searched_profile[4],
                    }]).set_index("Id")
                    st.dataframe(dataframe)
                else:
                    st.warning("No profile found with that email.")
    else:
        st.warning("Please log in first.")
        st.markdown("[Go to User Profile page](User_Profile_SignIn)")

def user_authentication(user_id: int, user_email: str):
    """Checks if the user with the given user_id and user_email exists and is authorized.
    Args:
        user_id (int): Unique identifier for the user.
        user_email (str): Email address of the user.
    Returns:
        bool: True if the user is authorized, False otherwise.
    """
    db = DataBaseManagement()
    profile = db.get_user_profile(user_id=user_id, email=user_email)
    return bool(profile)

profile_page()

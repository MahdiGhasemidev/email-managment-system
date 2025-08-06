import streamlit as st

from utils.db import DataBaseManagement

st.set_page_config(page_title="Profiles", page_icon=":zap:")

def user_authentication(user_email):
    """Checks if the user with the given user_id and user_email exists and is authorized.
    Args:
    user_id (int): Unique identifier for the user.
    user_email (str): Email address of the user.
    Returns:
    bool: True if the user is authorized, False otherwise.
    """
    db = DataBaseManagement()
    user_id = db.get_user_id_by_email(user_email)
    if user_id is None:
        return False
    return bool(db.get_user_profile(user_id=user_id, email=user_email))

def email_templates():
    if "user_email" not in st.session_state:
        st.warning("Please log in first.")
        st.markdown("[Go to User Profile page](User_Profile_SignIn)")
        return

    if not user_authentication(st.session_state.user_email):
        st.warning("Please fill user profile form in 'User Profile' page first.")
        st.markdown("[Go to User Profile page](User_Profile_SignIn)")
        return

    db = DataBaseManagement()
    user_email = st.session_state.user_email
    user_id = db.get_user_id_by_email(user_email)

    #* Show templates after when user logged in...
    if "template_success_msg" in st.session_state:
        st.success(st.session_state["template_success_msg"])
        del st.session_state["template_success_msg"]
    if "template_error_msg" in st.session_state:
        st.error(st.session_state["template_error_msg"])
        del st.session_state["template_error_msg"]

    st.markdown("## Add an Email Template 🔖")
    st.markdown("##### Add templates you use more, This will make it easier to send emails")

    with st.form(key="Email Template"):
        template_name = st.text_input("Template name", placeholder="Choose a name for the template...")
        template_body = st.text_area("Template body", height=200, placeholder="Dear Mr...")
        if st.form_submit_button("Submit"):
            if template_body.strip():
                results = db.add_template(name=template_name, body=template_body, user_id=user_id)
                if results:
                    st.session_state["template_success_msg"] = "✅ Template added successfully!"
                else:
                    st.session_state["template_error_msg"] = "❌ Failed to add template"
                st.experimental_rerun()
            else:
                st.error("❌ Please fill in all fields")

    st.header("Existing Templates")
    templates = db.get_all_templates(user_id)
    if not templates:
        st.info("No templates found. Add a new template above.")
    else:
        for template in templates:
            template_id = template[0]
            template_name = template[1]
            template_body = template[2]
            with st.expander(f"Template: {template_name}"):
                st.write("**Template ID:**", template_id)
                st.text_area("", value=template_body, height=150, key=f"Body_{template_id}", disabled=True)

    delete_id = st.text_input("Enter Template ID to Delete", placeholder="Enter ID to delete template")
    delete_clicked = st.button("Delete Template")
    if delete_clicked:
        if not delete_id:
            st.error("❌ Please enter a template ID to delete.")
        else:
            try:
                delete_id_int = int(delete_id)
                #* check if template exists before deleting
                existing_template = [t for t in templates if t[0] == delete_id_int]
                if not existing_template:
                    st.error(f"❌ No template found with ID {delete_id_int}")
                else:
                    result = db.delete_template(delete_id_int, user_id)
                    if result:
                        st.success(f"✅ Template with ID {delete_id_int} deleted successfully")
                        st.experimental_rerun()
                    else:
                        st.error(f"❌ Failed to delete template with ID {delete_id_int}")
            except ValueError:
                st.error("❌ Please enter a valid ID")

if __name__ == "__main__":
    email_templates()

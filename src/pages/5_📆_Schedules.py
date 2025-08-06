from datetime import datetime

import pytz
import streamlit as st

from utils.db import DataBaseManagement

st.set_page_config(page_title="Schedules", page_icon="📅")

def page_schedules():
    if "user_email" not in st.session_state:
        st.warning("Please log in first.")
        return

    if user_authentication(st.session_state.user_id, st.session_state.user_email):
        db = DataBaseManagement()
        st.markdown("## 📅 Scheduled Emails")
        st.markdown("##### Here you can view and manage upcoming scheduled emails")

        all_schedules = db.get_all_schedules()

        if not all_schedules:
            st.info("No scheduled emails found.")
            return

        tehran_tz = pytz.timezone("Asia/Tehran")
        now_tehran = datetime.now(tehran_tz)

        upcoming_schedules = []
        for s in all_schedules:
            scheduled_date = s[1]
            if scheduled_date.tzinfo is None:
                scheduled_date = tehran_tz.localize(scheduled_date)
            if scheduled_date > now_tehran:
                upcoming_schedules.append((s[0], scheduled_date))

        if not upcoming_schedules:
            st.info("There are no upcoming scheduled emails.")
            return

        for schedule in upcoming_schedules:
            email_id = schedule[0]
            scheduled_date = schedule[1]

            email_info = db.get_sent_email(email_id)
            if email_info:
                recipient = email_info[1]   # Recipients
                subject = email_info[2]     # Subject

                with st.container():
                    st.write(f"**To:** {recipient}")
                    st.write(f"**Subject:** {subject}")
                    st.write(f"**Scheduled Date:** {scheduled_date}")

                    if st.button(f"❌ Cancel Schedule #{email_id}", key=f"cancel_{email_id}"):
                        db.delete_schedule(email_id)
                        st.success(f"Schedule #{email_id} canceled.")
                        st.experimental_rerun()


def user_authentication(user_id, user_email):
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


if __name__ == "__main__":
    page_schedules()

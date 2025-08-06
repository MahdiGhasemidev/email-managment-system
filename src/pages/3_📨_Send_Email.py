from datetime import datetime
import pytz
import streamlit as st
import re

from utils.db import DataBaseManagement
from utils.decandenc import decrypt, generate_key
from utils.send_mail import send_email
from utils.reg_engine import generate_email_with_rag

st.set_page_config(page_title="Send Email", page_icon="📨")


def replace_placeholders_in_body(template_body, profile_data):
    lowered_profile = {k.lower(): str(v) if v is not None else "" for k, v in profile_data.items()}
    return re.sub(r"[\{\[]\s*(\w+)\s*[\}\]]", lambda m: lowered_profile.get(m.group(1).lower(), ""), template_body)


def user_authentication(user_id, user_email):
    db = DataBaseManagement()
    return bool(db.get_user_profile(user_id, user_email))


def send_email_page():
    if "user_email" not in st.session_state or "user_id" not in st.session_state:
        st.warning("Please log in first.")
        return

    if not user_authentication(st.session_state.user_id, st.session_state.user_email):
        st.warning("Please log in first.")
        return

    db = DataBaseManagement()
    sender_email = st.session_state.user_email
    user_profile = db.get_user_profile(st.session_state.user_id, sender_email)
    sender_password = decrypt(user_profile[6], generate_key("securepassword"))

    templates = db.get_all_templates(st.session_state.user_id)
    profiles = db.get_all_profiles(st.session_state.user_id)

    st.markdown("# Send Emails 📧")
    st.markdown("### Send emails to one or many profiles you wish")
    st.markdown("### You could choose templates too!")
    st.markdown("#### What are you waiting for!?")
    st.markdown("---" * 30)

    email_options = [prof[2] for prof in profiles] if profiles else []
    if not email_options:
        st.info("No profiles found to send emails to.")
        return
    if "use_rag" not in st.session_state:
        st.session_state["use_rag"] = False

    if "email_body" not in st.session_state:
        st.session_state["email_body"] = ""

    if "preview_body" not in st.session_state:
        st.session_state["preview_body"] = ""

    with st.form("send_email_form"):
        selected_emails = st.multiselect("Select recipients", options=email_options)
        subject = st.text_input("Subject", placeholder="Enter subject of email")

        template_options = ["None"] + [temp[1] for temp in templates]
        selected_template = st.selectbox("Select a template", options=template_options)

        if selected_template == "None":
            st.session_state["email_body"] = st.text_area("Email Body", height=200, value=st.session_state["email_body"], placeholder="Write your email body here...")
        else:
            st.session_state["email_body"] = ""  # قالب هست، متن دستی نداریم

        uploaded_file = st.file_uploader("Upload media (optional)", type=["jpg", "png", "pdf", "mp4"])

        selected_date = st.date_input("Select scheduled send date (optional)", value=None)
        selected_time = st.time_input("Select scheduled send time (optional)", value=None)

        preview_clicked = st.form_submit_button("Preview Template")
        send_clicked = st.form_submit_button("Send Email")

    if preview_clicked:
        if selected_template != "None":
            st.session_state["preview_body"] = next((temp[2] for temp in templates if temp[1] == selected_template), "")
        else:
            st.session_state["preview_body"] = st.session_state["email_body"]

    if st.session_state["preview_body"]:
        st.text_area("Email Body Preview", value=st.session_state["preview_body"], height=200)

    # دکمه های rag خارج فرم:
    if st.button("🔄 Toggle RAG (Current: ON)" if st.session_state["use_rag"] else "🔄 Toggle RAG (Current: OFF)"):
        st.session_state["use_rag"] = not st.session_state["use_rag"]

    if st.session_state["use_rag"]:
        casual_tone = st.checkbox("Use casual tone (if unchecked, formal tone is used)")
        tone = "casual" if casual_tone else "formal"

        if st.button("Generate Email Suggestion (RAG)"):
            base_text = st.session_state["email_body"] if selected_template == "None" else st.session_state["preview_body"]
            if base_text.strip():
                with st.spinner("Generating smart suggestion with RAG..."):
                    rag_result = generate_email_with_rag(base_text, title=subject, tone=tone)
                st.subheader("📩 پیشنهاد ایمیل هوشمند (RAG):")
                st.text_area("RAG Suggested Email", value=rag_result, height=200)
            else:
                st.warning("Please write or select an email body before generating suggestions.")
        # ================== پردازش ارسال ایمیل ==================
    if send_clicked:
        if not selected_emails:
            st.error("Please select at least one recipient.")
            return
        if not subject:
            st.error("Please enter the email subject.")
            return

        selected_template_body = ""
        if selected_template != "None":
            selected_template_body = next((temp[2] for temp in templates if temp[1] == selected_template), "")

        # ساخت بدنه نهایی ایمیل‌ها
        final_bodies = {}
        for email in selected_emails:
            prof = next((p for p in profiles if p[2] == email), None)
            profile_data = {"name": prof[1], "title": prof[3], "profession": prof[4]} if prof else {}
            body = replace_placeholders_in_body(email_body, profile_data) if selected_template == "None" \
                else replace_placeholders_in_body(selected_template_body, profile_data)
            final_bodies[email] = body

        # زمان‌بندی
        tehran_tz = pytz.timezone("Asia/Tehran")
        scheduled_date = None
        if selected_date and selected_time:
            scheduled_date = tehran_tz.localize(datetime.combine(selected_date, selected_time))
            if scheduled_date < datetime.now(tehran_tz):
                st.warning("Selected date is in the past.")
                scheduled_date = None

        # ارسال یا زمان‌بندی
        if scheduled_date is None:
            with st.spinner("Sending emails..."):
                for email, body in final_bodies.items():
                    result = send_email(sender_email, sender_password, subject, [email], body, uploaded_file)
                    db.add_sent_email(email, subject, body, datetime.now(tehran_tz), st.session_state.user_id)
                    if result:
                        st.success(f"✅ Email sent to {email}")
                    else:
                        st.error(f"❌ Failed to send email to {email}")
        else:
            with st.spinner("Scheduling emails..."):
                for email, body in final_bodies.items():
                    email_id = db.add_sent_email(email, subject, body, None, st.session_state.user_id)
                    if email_id:
                        db.add_schedule(email_id=email_id, scheduled_date=scheduled_date, user_id=st.session_state.user_id)
                st.success(f"📅 Emails scheduled for {scheduled_date.strftime('%Y-%m-%d %H:%M:%S')}.")


if __name__ == "__main__":
    send_email_page()

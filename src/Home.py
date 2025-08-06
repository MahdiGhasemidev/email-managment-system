from datetime import datetime
import pandas as pd
import pytz
import streamlit as st
from utils.db import DataBaseManagement
from utils.decandenc import decrypt, generate_key
from utils.send_mail import send_email

st.set_page_config(page_title="Email Management System", page_icon=":Home:")
st.image("./image/2.jpeg", use_column_width=True)

# ---------------- Helper ----------------
def make_aware(dt):
    tehran_tz = pytz.timezone("Asia/Tehran")
    if dt is None:
        return None
    return dt if dt.tzinfo else tehran_tz.localize(dt)

# ---------------- Main Page ----------------
def main_page():
    if "last_success_message" in st.session_state:
        st.success(st.session_state["last_success_message"])
        del st.session_state["last_success_message"]

    if "user_email" in st.session_state and "user_id" in st.session_state:
        if user_authentication(st.session_state.user_id, st.session_state.user_email):
            db = DataBaseManagement()
            user_profile = db.get_user_profile(st.session_state.user_id, st.session_state.user_email)
            user_name = user_profile[1]

            # 🔹 نمایش تعداد ایمیل‌های جدید
            new_email_count = db.get_newly_sent_emails_count(st.session_state.user_email)
            if new_email_count > 0:
                st.info(f"📬 {new_email_count} new scheduled email(s) sent in the last 24 hours!")
                db.mark_emails_as_notified(st.session_state.user_email)

            # 🔹 آمار ایمیل‌ها
            email_data = get_sent_email_statistics(st.session_state.user_email)
            if email_data:
                st.title(f"Welcome, {user_name} :crown:")
                col1, col2 = st.columns([2, 1])

                # ---------------- Last 10 Sent Emails ----------------
                with col1:
                    st.subheader("Last 10 Sent Emails")
                    sent_emails = db.get_all_sent_emails(st.session_state.user_id)
                    sent_emails = sent_emails[-10:] if sent_emails else []
                    if sent_emails:
                        df = pd.DataFrame(sent_emails, columns=[
                            "Email_id", "Recipients", "Subject", "Body", "Sent_date", "notified", "user_id",
                        ]).set_index("Email_id")
                        st.dataframe(df[["Recipients", "Subject", "Sent_date"]].style.format({
                            "Sent_date": lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if pd.notnull(x) else ""
                        }))
                    else:
                        st.write("No emails sent yet.")

                # ---------------- Upcoming Reminders & Schedules ----------------
                with col2:
                    st.subheader("Upcoming Scheduled Emails")
                    # حالا فقط از جدول Schedules استفاده می‌کنیم
                    schedules = db.get_all_schedules()
                    now_tehran = datetime.now(pytz.timezone("Asia/Tehran"))

                    # جدا کردن تاریخ‌های آینده
                    upcoming_schedules = [s for s in schedules if s[1] and make_aware(s[1]) > now_tehran]
                    if upcoming_schedules:
                        for schedule in upcoming_schedules:
                            email_id = schedule[0]
                            scheduled_time = make_aware(schedule[1])
                            email_info = db.get_sent_email(email_id)
                            if email_info:
                                recipient = email_info[1]
                                subject = email_info[2]
                                st.write(f"📨 To: {recipient} | 🧾 Subject: {subject} | 🕒 At: {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
                            else:
                                st.write(f"Email ID {email_id} → Scheduled for: {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
                    else:
                        st.write("No upcoming scheduled emails.")

                    # 🔹 ایمیل‌های سررسیدشده (Due)
                    due_schedules = [s for s in schedules if s[1] and make_aware(s[1]) <= now_tehran]
                    if due_schedules:
                        st.markdown("**⏱ Sending Due Scheduled Emails...**")
                        sent_any = False
                        for schedule in due_schedules:
                            email_id = schedule[0]
                            email_info = db.get_sent_email(email_id)
                            if email_info:
                                recipient = email_info[1]
                                subject = email_info[2]
                                body = email_info[3]
                                notified = email_info[5]  # ستون notified

                                if not notified:
                                    user_profile = db.get_user_profile(st.session_state.user_id, st.session_state.user_email)
                                    sender_email = st.session_state.user_email
                                    sender_password = decrypt(user_profile[6], generate_key("securepassword"))

                                    send_result = send_email(
                                        sender_email=sender_email,
                                        sender_password=sender_password,
                                        subject=subject,
                                        to=[recipient],
                                        contents=body,
                                        attachments=None,
                                    )

                                    if send_result:
                                        db.update_sent_email_date(email_id=email_id, sent_date=now_tehran)
                                        db.mark_email_as_notified(email_id)
                                        st.session_state["last_success_message"] = f"✅ Sent scheduled email to {recipient} (Subject: {subject})"
                                        sent_any = True
                                    else:
                                        st.error(f"❌ Failed to send email to {recipient}")
                        if sent_any:
                            st.experimental_rerun()

                    # 🔹 ایمیل‌های آینده
                    upcoming_schedules = [s for s in schedules if s[1] and make_aware(s[1]) > now_tehran]
                    if upcoming_schedules:
                        st.markdown("**Scheduled Emails:**")
                        for s in upcoming_schedules:
                            email_id = s[0]
                            scheduled_time = make_aware(s[1])
                            email_info = db.get_sent_email(email_id)
                            if email_info:
                                st.write(f"📨 To: {email_info[1]} | 🧾 Subject: {email_info[2]} | 🕒 At: {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
                            else:
                                st.write(f"Email ID {email_id} → Scheduled for: {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
                    else:
                        st.write("No upcoming scheduled emails.")

                # ---------------- Email Statistics ----------------
                st.markdown("--" * 30)
                st.subheader("Email Statistics")
                total_sent = email_data["Total Sent"]
                successful_sent = email_data["Successful Sent"]
                failed_sent = email_data["Failed Sent"]
                success_pct = (successful_sent / total_sent) * 100 if total_sent else 0
                fail_pct = (failed_sent / total_sent) * 100 if total_sent else 0

                c1, c2, c3 = st.columns(3)
                c1.metric("Sent Emails", f"{total_sent} emails")
                c2.metric("Successful", f"{success_pct:.2f}%", delta="↑")
                c3.metric("Failed", f"{fail_pct:.2f}%", delta="↓")

    else:
        st.warning("Please log in first.")
        st.markdown("[Go to User Profile page](User_Profile_SignIn)")

# ---------------- Authentication ----------------
def user_authentication(user_id, user_email):
    db = DataBaseManagement()
    return bool(db.get_user_profile(user_id, user_email))

def get_sent_email_statistics(user_email):
    return {"Total Sent": 25, "Failed Sent": 2, "Successful Sent": 23}

# ---------------- Login ----------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    user_email = st.text_input("Please Enter your email")
    user_password = st.text_input("Please Enter your password", type="password")

    if st.button("Login"):
        db = DataBaseManagement()
        if db.authenticate_user(user_email, user_password):
            user_id = db.get_user_id_by_email(user_email)
            st.session_state.logged_in = True
            st.session_state.user_email = user_email
            st.session_state.user_id = user_id
            st.success("Logged in successfully!")
            st.experimental_rerun() 
        else:
            st.error("Invalid email or password!")
else:
    main_page()


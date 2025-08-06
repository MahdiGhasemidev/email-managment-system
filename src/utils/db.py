import re
from datetime import datetime

import mariadb
from loguru import logger

from utils.decandenc import decrypt, generate_key

""" Database management utilities for EMS.

    This module provides the DataBaseManagement class, which encapsulates all database operations
    for the EMS application, including user profiles, email templates, sent emails, reminders,
    schedules, and social media links. It uses MariaDB for storage and supports encryption for
    user passwords.

    Classes:
        DataBaseManagement: Handles all CRUD operations for EMS database tables.

    Functions:
        parse_datetime_repr(text): Safely parses a string representation of a datetime object.

    Dependencies:
        - mariadb
        - loguru
        - utils.decandenc (encrypt, generate_key, decrypt)
        - hashlib
        - datetime
        - re
"""


def parse_datetime_repr(text):
    """ Parse string like 'datetime.datetime(2025, 7, 25, 18, 9)' safely """
    match = re.match(r"datetime\.datetime\((\d+), (\d+), (\d+), (\d+), (\d+)\)", text)
    if match:
        parts = [int(p) for p in match.groups()]
        return datetime(*parts)
    return None


class DataBaseManagement:
    def __init__(self):
        """Data base management for EMS
        """
        #! Connect to database
        try:
            self.conn = mariadb.connect(
                user="root",
                password="",
                host="localhost",
                database="EMSdb",
            )
            self.cursor = self.conn.cursor()
            self.create_tables()

        except mariadb.Error as e:
            logger.success(f"Error connecting to MariaDB: {e}")

    def create_tables(self):
            """Creates necessary tables in the database if they don't exist.
            The tables created include:
            - Profiles: Stores information about profiles.
            - Templates: Stores email templates.
            - Sent_Emails: Stores sent email records.
            - Reminders: Stores email reminder information.
            - Schedules: Stores email scheduling information.
            - User_profile: Stores user profile information with encrypted password.
            - Social_media: Stores social media links for each user.
            """
            try:
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Profiles (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        Name VARCHAR(100),
                        Email VARCHAR(100),
                        Title VARCHAR(200),
                        Profession VARCHAR(100)
                    );
                """)
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Templates (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        Name VARCHAR(100),
                        Body VARCHAR(500)
                    );
                """)
                self.cursor.execute("""
                                    CREATE TABLE IF NOT EXISTS Sent_Emails(
                                        Email_id INT AUTO_INCREMENT PRIMARY KEY,
                                        Recipients VARCHAR(200),
                                        Subject VARCHAR(100),
                                        Body VARCHAR(500),
                                        Sent_date DATETIME
                                    );
                                    """)
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Reminders (
                        Email_id INT,
                        Remind_date DATETIME,
                        FOREIGN KEY (Email_id) REFERENCES Sent_Emails(Email_id)
                    );
                """)
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Schedules (
                        Email_id INT,
                        Scheduled_date DATETIME,
                        FOREIGN KEY (Email_id) REFERENCES Sent_Emails(Email_id)
                    );
                """)
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS User_profile (
                        User_id INT AUTO_INCREMENT PRIMARY KEY,
                        Name VARCHAR(100),
                        Title VARCHAR(200),
                        Proffesion VARCHAR(100),
                        Signiture VARCHAR(100),
                        Email VARCHAR(100) UNIQUE,
                        Encrypted_password VARCHAR(200) NOT NULL
                    );
                    """)
                self.cursor.execute("""
                                    CREATE TABLE IF NOT EXISTS Social_media(
                                        User_id int,
                                        LinkedIn VARCHAR(200),
                                        X VARCHAR(200),
                                        Telegram VARCHAR(200),
                                        Github VARCHAR(200),
                                        FOREIGN KEY (User_id) REFERENCES User_profile(User_id)
                                    );
                                    """)

                self.conn.commit()
                logger.success("Tables created successfully")

            except mariadb.Error as e:
                logger.error(f"Error creating tables: {e}")

    def add_profile(self, name:str , email: str, title: str, proffesion: str, user_id: int) -> bool:
        """ Add a profile to the database.
        """
        try:
            sql = """
                    INSERT INTO Profiles (Name, Email, Title, Profession, User_id) VALUES (? , ? ,? ,?, ?)
                    """
            self.cursor.execute(sql,(name, email, title,proffesion, user_id ))
            self.conn.commit()

        except Exception as e:
            logger.error(f"Failed to add profile \n {e}")
            return False

        else:
            return True

    def get_profile(self, email: str, user_id: int) -> tuple :
        """ Retrieve a profile by ID.
        """
        try:
            sql = " SELECT * FROM Profiles WHERE Email = %s AND User_id = %s"
            self.cursor.execute(sql,(email,user_id))
            return self.cursor.fetchone()

        except Exception as e:
            logger.error(f"Failed to show {email} to you \n {e}")
            return False

        else:
            return True

    def update_profile(self, profile_id: int, name: str, email: str, title: str, profession: str) -> bool:
        """ Update a profile by ID
        """
        try:
            sql = """UPDATE Profiles
                    SET Name = ?, Email = ?, Title = ?, Profession = ?
                    WHERE id = ?"""
            self.cursor.execute(sql, (name, email, title, profession, profile_id))
            self.conn.commit()

            #! checks the row to make sure upadate has been done correctly :

            if self.cursor.rowcount > 0:
                logger.success(f"Profile with ID {profile_id} updated successfully")
                return True
            logger.warning(f"Profile with ID {profile_id} not found")
            return False

        except Exception as e:
            logger.error(f"Failed to update profile: {e}")
            return False
        else:
            return True

    def delete_profile(self, profile_id: int) -> bool:
        """ Delete a profile by ID
        """
        try:
            sql = "DELETE FROM Profiles WHERE id = ? "
            self.cursor.execute(sql, (profile_id,))
            self.conn.commit()
            logger.success(f"{profile_id} Deleted successfuly")

        except Exception as e:
            logger.error(f"Failed to delete {profile_id} \n {e}")
            return False

        else:
            return True

    def get_all_profiles(self, user_id: int):
        """Retrieve all profiles belonging to a specific user."""
        sql = "SELECT * FROM Profiles WHERE user_id = ?"
        self.cursor.execute(sql, (user_id,))
        return self.cursor.fetchall()

    def add_template(self, name: str, body: str, user_id: int) -> bool:
        """ Add a template to Templates table in db
        """
        try:
            sql = """
                    INSERT INTO Templates (Name, Body, User_id) VALUES (? , ?, ?)
            """
            self.cursor.execute(sql, (name, body, user_id))
            self.conn.commit()
            logger.success("Values Inserted Successfuly")

        except Exception as e:
            logger.error(f"Something went wrong! \n {e}")
            return False

        else:
            return True

    def get_all_templates(self, user_id: int) -> tuple:
        """ Retrieve all templates form Templates table
        """
        sql = "SELECT * FROM Templates WHERE User_id = ?"
        self.cursor.execute(sql, (user_id,))
        return self.cursor.fetchall()

    def delete_template(self, template_id: int, user_id:int) -> bool:
        """ Delete a template by ID
        """
        try:
            sql = "DELETE FROM Templates WHERE id = ? AND User_id = ?"
            self.cursor.execute(sql, (template_id,user_id))
            self.conn.commit()
            logger.success(f"{template_id} Deleted successfuly")

        except Exception as e :
            logger.error(f"{template_id} Dosen't exists ! \n {e}")
            return False

        else:
            return True

    def add_sent_email(self, recipients: str, subject: str, body: str, sent_date: str, user_id) -> bool:
        """ Add a sent email to Sent_Emails table in db
        """
        try:
            sql = "INSERT INTO Sent_Emails(Recipients, Subject, Body, Sent_date, User_id) VALUES (?, ?, ?, ?, ?)"
            self.cursor.execute(sql, (recipients, subject, body, sent_date, user_id))
            self.conn.commit()
            email_id = self.cursor.lastrowid
            logger.success("Email_sent Successfuly added")
            return email_id

        except Exception as e:
            logger.error(f"Failed to add_sent_email {e}")
            return False

        else:
            return True

    def get_sent_email(self, email_id: int) -> tuple:
        """ Retrieve a sent email by ID
        """
        sql = " SELECT * FROM Sent_Emails Where Email_id = ?"
        self.cursor.execute(sql, (email_id,))
        return self.cursor.fetchone()

    # def update_sent_email_date(self, email_id: int, sent_date):
    #     sql = "UPDATE Sent_Emails SET Sent_date=%s WHERE Email_id=%s"
    #     self.cursor.execute(sql, (sent_date, email_id))
    #     self.conn.commit()

    def mark_email_as_notified(self, email_id: int):
        sql = "UPDATE Sent_Emails SET notified=1 WHERE Email_id=%s"
        self.cursor.execute(sql, (email_id,))
        self.conn.commit()

    def get_all_sent_emails(self, user_id: int):
        sql = "SELECT * FROM Sent_Emails WHERE user_id=%s ORDER BY Sent_date DESC"
        self.cursor.execute(sql, (user_id,))
        return self.cursor.fetchall()

    def get_all_sent_emails(self, user_id: int):
        """ Retrieve all sent_emails
        """
        sql = "SELECT * FROM Sent_Emails WHERE User_id = %s ORDER BY Sent_date DESC"
        self.cursor.execute(sql,(user_id,))
        return self.cursor.fetchall()

    def get_user_id_by_email(self, email: str) -> int | None:
        sql = "SELECT User_id FROM User_profile WHERE Email = %s"
        self.cursor.execute(sql, (email,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def add_reminder(self, email_id: int, reminder_date: str) -> bool :
        """ Add a reminder to Reminders table in db
        """
        try:
            sql = "INSERT INTO Reminders(Email_id ,Remind_date) VAlUES (?, ? )"
            self.cursor.execute(sql, (email_id,reminder_date))
            self.conn.commit()
            logger.success("Reminder Created Successfuly")
        except Exception as e :
            logger.error(f"Failed to create reminder! Becauese of : {e}")
            return False

        else:
            return True

    def get_all_reminders(self) -> tuple:
        """ Retrieve all reminders from Reminders table
        """
        try:
            sql = "SELECT * FROM Reminders"
            self.cursor.execute(sql)
            logger.success("Here is all your reminders ")
            return self.cursor.fetchall()

        except Exception as e:
            logger.error(f"OOPS! Something went wrong! {e}")
            return False

        else:
            return True

    def get_reminder(self, email_id: int) -> tuple :
        """ Retrieve a reminder by ID
        """
        try:
            sql = "SELECT * FROM Reminders WHERE Email_id = ?"
            self.cursor.execute(sql, (email_id,))
            return self.cursor.fetchone()

        except Exception as e:
            logger.error(f"OOPS! Something went wrong! {e}")
            return False

        else:
            return True

    def delete_reminder(self, email_id: int) -> bool:
        """ Delete a reminder by ID
        """
        try:
            sql = """ DELETE FROM Reminders WHERE Email_id = ?"""
            self.cursor.execute(sql, (email_id,))
            self.conn.commit()
            logger.success(f"{email_id} DELETED Successfuly ! ")

        except Exception as e :
            logger.error(f"OOPS! Something went wront {e}")
            return False

        else:
            return True

    def update_reminder(self, email_id : int, remind_date: str) -> bool :
        """ Update a reminder by ID
        """
        try:
            sql = """UPDATE Reminders
                    SET Remind_date = ?
                    WHERE id = ?"""
            self.cursor.execute(sql, (email_id, remind_date))
            self.conn.commit()

            if self.cursor.rowcount > 0 :
                logger.success(f"{email_id}'s Reminder updated successfuly")
                return True

            logger.error(f"{email_id} Not found!")
            return False

        except Exception as e :
            logger.error(f"Failed to update {email_id} reminder! {e}")
            return False

        else:
            return True

    def add_schedule(self, email_id: int, scheduled_date: datetime, user_id: int) -> bool :
        """ Add a schedule to Schedules table in db
        """
        try:
            sql = "INSERT INTO Schedules(Email_id, Scheduled_date, User_id) VALUES (? , ?, ?) "
            self.cursor.execute(sql, (email_id, scheduled_date, user_id))
            self.conn.commit()
            logger.success(f"Schedulde date {scheduled_date} setted up successfuly")

        except Exception as e:
            logger.error(f"OOOPPS! Soemthing went wrong!!! \n {e}")
            return False

        else:
            return True


    def get_schedule(self, email_id: int) -> tuple:
        """ Retrieve a schedule by ID.
        """
        try:
            sql = "SELECT * FROM Schedules WHERE Email_id = ? "
            self.cursor.execute(sql, (email_id,))
            return self.cursor.fetchone()

        except Exception as e :
            logger.error(f"OOOPPS! Something went wrong ! \n {e}")
            return False

        else:
            return True

    def delete_schedule(self, email_id: int) -> bool :
        """ deletea a schedule by ID
        """
        try:
            sql = "DELETE FROM Schedules WHERE Email_id = ?"
            self.cursor.execute(sql, (email_id,))
            self.conn.commit()
            logger.success(f"{email_id} Schedule deleted successfuly ! ")

        except Exception as e:
            logger.error(f"OOOPPS! Something went wrong! {e}")
            return False

        else:
            return True

    def update_schedule(self, email_id: int, scheduled_date: str) -> bool :
        """ Update a schedule by ID
        """
        try:
            sql = """UPDATE Schedules
                SET Scheduled_date = ?
                WHERE Email_id = ?
                """
            self.cursor.execute(sql, (email_id, scheduled_date))
            self.conn.commit()
            logger.success(f"{email_id} Scheduled_date Updated Successfuly!")

        except Exception as e:
            logger.error(f"OOPPS! Something went wrong! {e}")
            return False

        else:
            return True

    def get_all_schedules(self) -> list:
        """ Retrieve all schedules with correct datetime parsing """
        try:
            sql = "SELECT * FROM Schedules"
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            schedules = []
            for row in rows:
                email_id = row[0]
                sched_date = row[1]
                if isinstance(sched_date, str) and sched_date.startswith("datetime.datetime"):
                    sched_date = parse_datetime_repr(sched_date)
                schedules.append((email_id, sched_date))
            return schedules
        except Exception as e:
            logger.error(f"OOPS! Something went wrong! {e}")
            return []
        else:
            return True

    def set_user_profile(self, name: str, title: str, proffesion: str,
                        signiture: str, email: str,encrypted_password: str,
                        ) -> bool:
        """ Add a user profile to User_profile table in db
        """
        try:
            sql = """ INSERT INTO
            User_profile(Name, Title, Proffesion, Signiture, Email, Encrypted_password)
            VALUES(?, ?, ?, ?, ?, ?)
            """
            self.cursor.execute(sql, (name, title, proffesion, signiture, email, encrypted_password))
            self.conn.commit()
            logger.success(f"User : {name} Added Successfuly")

        except Exception as e:
            logger.error(f"OOOPPS! Something went wrong {e}")
            return False

        else:
            return True

    def get_user_profile(self, user_id: int, email: str) -> tuple:
        """Retrieve a user profile by ID and Email"""
        try:
            sql = "SELECT * FROM User_profile WHERE User_id = %s AND Email = %s"
            self.cursor.execute(sql, (user_id, email))
            return self.cursor.fetchone()

        except Exception as e:
                logger.error(f"Failed to retrieve user profile for {email} (ID: {user_id})\n{e}")
                return False

        else:
                return True

    def get_all_user_profile(self) -> tuple:
        """ Retrieve all user profiles
        """
        try:
            sql = "SELECT * FROM User_profile"
            self.cursor.execute(sql)
            return self.cursor.fetchall()

        except Exception as e:
            logger.error(f"OOPPS! Something went wrong sir/miss ! {e}")
            return False

        else:
            return True

    def delete_user(self, user_id: int) -> bool:
        """ Delete user from User_proile table by ID
        """
        try:
            sql = "DELETE FROM User_profile WHERE User_id = ?"
            self.cursor.execute(sql, (user_id,))
            self.conn.commit()
            logger.success(f"{user_id} Deleted successfuly!")


        except Exception as e:
            logger.error(f"OOPPS! Something went wrong sir/miss ! {e}")
            return False

        else:
            return True

    def update_user(self, user_id: int, name: str, title: str,
                    proffesion: str, signiture: str, email:str, encrypted_password: str,
                    ) -> bool:
        """ Update user by ID
        """
        try:
            sql = """UPDATE User_profile
            SET Name = ?, Title = ? , Proffesion = ? ,
            Signiture = ? , Email = ?, Encrypted_password = ?
            WHERE User_id = ?
            """
            self.cursor.execute(sql, (name , title, proffesion, signiture, email, encrypted_password, user_id))
            self.conn.commit()
            logger.success(f"{user_id} {name} Information Updated Successfuly!")

        except Exception as e:
            logger.error(f"OOPPS! Something went wrong sir/miss ! {e}")
            return False

        else:
            return True

    def add_user_social_media(self, user_id: int, linkedin: str, x: str, telegram: str, github: str) -> bool:
        """ Add user social media accounts to Social_media table in db
        """
        try:
            sql= "INSERT INTO Social_media(LinkedIn, X, Telegram, Github) VALUES(?, ? , ?, ?) WHERE User_id = ?"
            self.cursor.execute(sql, (user_id, linkedin, x, telegram, github))
            self.conn.commit()
            logger.success(f"{user_id} social media inserted successfuly !")

        except Exception as e:
            logger.error(f"OOPPS! Something went wrong sir/miss ! {e}")
            return False

        else:
            return True

    def delete_user_social_media(self, user_id: int) -> bool:
        """ Delete user social media acounts by ID
        """
        try:
            sql= "DELETE FROM Social_media WHERE User_id = ?"
            self.cursor.execute(sql)
            self.conn.commit()
            logger.success(f"{user_id} Social Media Deleted successfuly ! ")

        except Exception as e:
            logger.error(f"OOPPS! Something went wrong sir/miss ! {e}")
            return False

        else:
            return True

    def get_user_social_media(self, user_id: int) -> tuple:
        """ Retrieve user social media accounts by ID
        """
        try:
            sql = "SELECT * FROM Social_media Where User_id = ?"
            self.cursor.execute(sql, (user_id))
            return self.cursor.fetchone()

        except Exception as e:
            logger.error(f"OOPPS! Something went wrong ! {e}")
            return False

        else:
            return True

    def authenticate_user(self, email: str, entered_password: str) -> bool:
        """Authenticates a user by verifying the entered password against the encrypted password stored in the database.

        Args:
            email (str): The email address of the user attempting to authenticate.
            entered_password (str): The password entered by the user.

        Returns:
            bool: True if authentication is successful, False otherwise.

        Raises:
            Exception: If an error occurs during database access or password decryption.
        """
        """"""
        try:
            sql = "SELECT Encrypted_password FROM User_profile WHERE Email = ?"
            self.cursor.execute(sql, (email,))
            result = self.cursor.fetchone()

            if result:
                encrypted_password = result[0]
                key = generate_key("securepassword")
                decrypted_password = decrypt(encrypted_password, key)
                if decrypted_password == entered_password:
                    return True
                return False
            return False
        except Exception as e:
            logger.error(f"Error: {e}")
            return False

    def get_newly_sent_emails_count(self, user_email):
        """count newly email sents
        """
        try:
            sql= """
                SELECT COUNT(*)
                FROM Sent_Emails
                WHERE Recipients = %s
                AND sent_date >= NOW() - INTERVAL 1 DAY
                AND notified = FALSE
            """
            self.cursor.execute(sql, (user_email,))
            result = self.cursor.fetchone()
            return result[0] if result else 0

        except Exception as e:
            logger.error(f"Somethin went wrong ! {e}")

    def mark_emails_as_notified(self, user_email):
        """mark sent email's as notified
        """
        try:
            sql = """
                UPDATE Sent_Emails
                SET notified = TRUE
                WHERE Recipients = %s
                AND sent_date >= NOW() - INTERVAL 1 DAY
                AND notified = FALSE
            """
            self.cursor.execute(sql, (user_email,))
            self.connection.commit()
        except Exception as e:
            logger.error(f"Something went wrong! {e}")


    def reset_sent_emails(self):
        """reset sent emails
        """
        try:
            self.cursor.execute("DELETE FROM Sent_Emails")
            self.cursor.execute("ALTER TABLE Sent_Emails AUTO_INCREMENT = 1")
            self.conn.commit()
            logger.success("SentEmails tables have been truncated and reset.")
        except Exception as e:
            logger.error(f"Error resetting tables: {e}")

    def reset_schedules(self):
        """resets schedules
        """
        try:
            self.cursor.execute("DELETE FROM Schedules")
            self.cursor.execute("ALTER TABLE Schedules AUTO_INCREMENT = 1")
            self.conn.commit()
            logger.success("Schedules table have been truncated and reset.")
        except Exception as e:
            logger.error(f"Error resetting tables: {e}")

    def update_sent_email_date(self, email_id: int, sent_date: datetime) -> bool:
        """update sent email date

        :param email_id: email id of sent email
        :type email_id: int
        :param sent_date: date that email sents
        :type sent_date: datetime
        :return: True or Flase
        :rtype: bool
        """
        try:
            sql = "UPDATE Sent_Emails SET Sent_date = ? WHERE Email_id = ?"
            self.cursor.execute(sql, (sent_date, email_id))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update Sent_date: {e}")
            return False



if __name__ == "__main__":
    #! create a object to use database
    db = DataBaseManagement()

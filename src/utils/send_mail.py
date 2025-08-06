import yagmail
from loguru import logger


def send_email(
            sender_email:str ,
            sender_password: str ,
            to: str ,
            subject: str ,
            contents: str ,
            attachments: list[str] | None = None,
            ) -> bool :
    """ Send an email using yagmail.

    :param sender_email: The email address of the sender.
    :type sender_email: str
    :param sender_password: The password of the sender's email account.
    :type sender_password: str
    :param to: The recipient's email address.
    :type to: str
    :param subject: The subject of the email.
    :type subject: str
    :param contents: The content of the email (can be text or HTML).
    :type contents: str
    :param attachments: A list of file paths to attach to the email, defaults to None.
    :type attachments: Optional[List[str]], optional
    :raises ValueError: If the sender's email or password is missing.
    :return: True if the email was sent successfully, False otherwise.
    :rtype: bool
    """
    try:
        _validate_credentials(sender_email=sender_email,sender_password=sender_password)
        with yagmail.SMTP(user = sender_email, password= sender_password) as yag:
            yag.send(
                to=to,
                contents=contents,
                subject=subject,
                attachments=attachments,
            )
        logger.success("Email Sent Successfully")
        return True

    except Exception as e:
        logger.error(f"An error occurred {e!s}")
        return False
    else:
        return True

def _validate_credentials(sender_email, sender_password):
    if not sender_email or not sender_password:
            raise ValueError("Sender Email or Password is Missing, Try again")

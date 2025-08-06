# ✉️ Email Management System

A powerful and user-friendly tool for managing and sending emails using [yagmail](https://github.com/kootenpv/yagmail). Easily send personalized emails to selected recipients, manage profiles, and automate your email workflow.

## 🚀 Features

- **Send emails to selected profiles**  
    Choose recipients from your saved profiles and send emails with ease.
- **Easy configuration with yagmail**  
    Simple setup for secure email sending.
- **Bulk emailing**  
    Send emails to multiple profiles at once.
- **Email scheduling**  
    Schedule emails to be sent at a later time.
- **Customizable templates**  
    Create and manage templates with dynamic placeholders (e.g., name, title).
- **Profile management**  
    Add, edit, or remove recipient profiles.
- **Intuitive Streamlit UI**  
    User-friendly web interface built with [Streamlit](https://streamlit.io/) for all operations.
- **Chatbot integration**  
    Use a chatbot to assist with composing and sending emails.
- **MariaDB database support**  
    Store and manage profiles, templates, and email logs securely using [MariaDB](https://mariadb.org/).


## Installation

```bash
pip install yagmail streamlit mysql-connector-python
```

## Usage

1. Configure your yagmail credentials (see [yagmail setup](https://github.com/kootenpv/yagmail#setup)).
2. Set up your MariaDB database and update the database connection settings in the project.
3. Run the Streamlit app:
    ```bash
    streamlit run main.py
    ```
4. Use the web interface to manage profiles, compose emails, and send or schedule messages.

## 🛠 Requirements

Dependencies are listed in `requirements.txt`.  
Install them with:

```bash
pip install -r requirements.txt
```

## 🪪 License

This project is licensed under the [MIT License](LICENSE).


## 👨‍💻 Author 
**Mahdi Ghasemi**  
📧 Email: mahdi.ghasemi.dev@gmail.com  
🌐 GitHub: [Mahdi Ghasemi](https://github.com/MahdiGhasemidev)  

---


### ⭐ If you find this project useful, give it a star!

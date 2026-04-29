# Teams AutoMeet 🤖

An advanced automation utility designed to handle Microsoft Teams meetings. It automates the process of logging in, joining via links or calendar events, maintaining privacy, tracking participant levels, and monitoring audio for specific triggers.

---

## ✨ Key Features

- **🔒 Stealth Operation:** Employs browser parameters designed to safely bypass automated software detectors.
- **🚀 Calendar & Link Integration:** Connects instantly using a provided URL or automatically identifies joinable instances on the Teams Dashboard.
- **🛡️ Automated Privacy:** Deactivates system video feeds and audio inputs natively prior to entry.
- **👥 Dynamic Roster Checking:** Exits calls systematically when user presence drops below the assigned threshold.
- **🎙️ AI Speech-To-Text (Whisper):** Records internal output seamlessly to build local logs.
- **🔔 Trigger Logic:** Evaluates text to send SMTP dispatches when flagged phrases arise.

---

## 📋 Prerequisites

Required installations:

- Python 3.8+
- Google Chrome

---

## 🚀 Installation & Setup

1. Extract the project source folder.
2. Open the command terminal within the directory.
3. Install prerequisites:
   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ Configuration Setup (`settings.toml`)

Open the configuration file to alter parameters:

```toml
email_id = "your-email@example.com"
password = "your-password"

meeting_link = "URL" # Optional

minimum_participants = 10
timeout = 60

whisper_model_size = "tiny"
alert_keywords = ["attendance"]

sender_email = "your-alerts-email@gmail.com"
sender_password = "app-password"
notification_email = "your-personal-email@gmail.com"
smtp_server = "smtp.gmail.com"
smtp_port = 587
```

---

## 💻 Usage

Execute the process via terminal:

```bash
python automeet.py
```

_Note: Allow administrative access initially for profile setups._

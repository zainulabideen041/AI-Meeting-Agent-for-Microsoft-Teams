import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from resources import data

def send_alert(keyword, transcript_snippet):
    try:
        sender_email = data.get('sender_email')
        sender_password = data.get('sender_password')
        target_email = data.get('notification_email')
        smtp_server = data.get('smtp_server', 'smtp.gmail.com')
        smtp_port = data.get('smtp_port', 587)

        if not all([sender_email, sender_password, target_email]):
            print("[Notifier] Missing email configuration. Skipping alert.")
            return

        subject = f"AutoMeet Alert: Keyword '{keyword}' Detected!"
        body = f"The word '{keyword}' was detected in your meeting.\n\nContext:\n... {transcript_snippet} ..."

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = target_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, target_email, text)
        server.quit()
        print(f"[Notifier] Alert email sent to {target_email}")
    except Exception as e:
        print(f"[Notifier] Failed to send email: {e}")

if __name__ == "__main__":
    # Test alert
    print("Testing notifier...")
    # send_alert("test", "This is a test transcript.")

import smtplib
from email.message import EmailMessage

EMAIL = "michealerinola9@gmail.com"
APP_PASSWORD = 'ebbjfztbsipaolpa'

msg = EmailMessage()
msg["Subject"] = "Direct Gmail Test"
msg["From"] = EMAIL
msg["To"] = EMAIL
msg.set_content("This is a direct SMTP test.")

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(EMAIL, APP_PASSWORD)
    server.send_message(msg)

print("SUCCESS")

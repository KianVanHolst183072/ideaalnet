import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, EmailStr

app = FastAPI(
    title="Email Notification API",
    description="Sends notification emails when a field is changed.",
    version="1.0.0",
)


class NotifyRequest(BaseModel):
    email: EmailStr
    field: str
    oldfield: str = ""
    newfield: str = ""


@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}


@app.post("/api/notify")
def notify(
    payload: NotifyRequest,
    x_api_key: str | None = Header(default=None),
):
    if x_api_key != os.environ.get("API_KEY"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        send_email(payload.email, payload.field, payload.oldfield, payload.newfield)
    except Exception as e:
        print(f"Email error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")

    return {"success": True}


def send_email(to_email: str, field: str, oldfield: str, newfield: str):
    host = os.environ["SMTP_HOST"]
    port = int(os.environ["SMTP_PORT"])
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASS"]
    sender = os.environ["SMTP_FROM"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Update to your {field}"
    msg["From"] = sender
    msg["To"] = to_email

    text = (
        f"Your {field} has been changed.\n\n"
        f"Old value: {oldfield}\n"
        f"New value: {newfield}"
    )
    html = (
        f"<p>Your <strong>{field}</strong> has been changed.</p>"
        f"<p><b>Old value:</b> {oldfield}<br/>"
        f"<b>New value:</b> {newfield}</p>"
    )
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    if port == 465:
        with smtplib.SMTP_SSL(host, port) as server:
            server.login(user, password)
            server.send_message(msg)
    else:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
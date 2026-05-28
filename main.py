import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/notify', methods=['POST'])
def notify():
    if request.headers.get('x-api-key') != os.environ.get('API_KEY'):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json(silent=True) or {}
    email = data.get('email')
    field = data.get('field')
    oldfield = data.get('oldfield', '')
    newfield = data.get('newfield', '')

    if not email or not field:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        send_email(email, field, oldfield, newfield)
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f'Email error: {e}')
        return jsonify({'error': 'Failed to send email'}), 500


def send_email(to_email, field, oldfield, newfield):
    host = os.environ['SMTP_HOST']
    port = int(os.environ['SMTP_PORT'])
    user = os.environ['SMTP_USER']
    password = os.environ['SMTP_PASS']
    sender = os.environ['SMTP_FROM']

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'Update to your {field}'
    msg['From'] = sender
    msg['To'] = to_email

    text = (
        f'Your {field} has been changed.\n\n'
        f'Old value: {oldfield}\n'
        f'New value: {newfield}'
    )
    html = (
        f'<p>Your <strong>{field}</strong> has been changed.</p>'
        f'<p><b>Old value:</b> {oldfield}<br/>'
        f'<b>New value:</b> {newfield}</p>'
    )
    msg.attach(MIMEText(text, 'plain'))
    msg.attach(MIMEText(html, 'html'))

    if port == 465:
        with smtplib.SMTP_SSL(host, port) as server:
            server.login(user, password)
            server.send_message(msg)
    else:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)


@app.route('/', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

from http.server import BaseHTTPRequestHandler
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Optional: shared-secret auth
        if self.headers.get('x-api-key') != os.environ.get('API_KEY'):
            return self._respond(401, {'error': 'Unauthorized'})

        # Parse JSON body
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError):
            return self._respond(400, {'error': 'Invalid JSON'})

        email = body.get('email')
        field = body.get('field')
        oldfield = body.get('oldfield', '')
        newfield = body.get('newfield', '')

        if not email or not field:
            return self._respond(400, {'error': 'Missing required fields'})

        try:
            self._send_email(email, field, oldfield, newfield)
            return self._respond(200, {'success': True})
        except Exception as e:
            print(f'Email error: {e}')
            return self._respond(500, {'error': 'Failed to send email'})

    def _send_email(self, to_email, field, oldfield, newfield):
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

    def _respond(self, status, payload):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())

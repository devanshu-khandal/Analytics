from flask import Flask, request, jsonify
import base64
from io import BytesIO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import logging

# Setup logging to file
logging.basicConfig(filename='app.log', level=logging.ERROR)

app = Flask(__name__)

def send_email(sender_email, receiver_email, cc_emails, bcc_emails, subject, message_body, smtp_config): #attachments
    # Create MIME message
    msg = MIMEMultipart()
    
    msg['From'] = sender_email
    
    # Ensure 'receiver_email', 'cc_emails', and 'bcc_emails' are always lists
    if not isinstance(receiver_email, list):
        receiver_email = [receiver_email]
    if not isinstance(cc_emails, list):
        cc_emails = []
    if not isinstance(bcc_emails, list):
        bcc_emails = []
    
    msg['To'] = ", ".join(receiver_email)
    msg['Cc'] = ", ".join(cc_emails)
    msg['Subject'] = subject
    
    if bcc_emails:
        msg['Bcc'] = ", ".join(bcc_emails)
    
    msg.attach(MIMEText(message_body, 'html'))

    # Attach files (if any)
    # for attachment in attachments:
    #     file_content = attachment['content']  # base64 encoded content
    #     file_name = attachment['filename']
    #     attach = MIMEApplication(file_content, _subtype=attachment.get('subtype', 'octet-stream'))
    #     attach.add_header('Content-Disposition', 'attachment', filename=file_name)
    #     msg.attach(attach)
    
    smtp_server = smtp_config['server']
    smtp_port = smtp_config['port']
    smtp_username = smtp_config['username']
    smtp_password = smtp_config['password']
    
    all_recipients = receiver_email + cc_emails + bcc_emails
    
    # Start SMTP connection
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, all_recipients, msg.as_string())

@app.route('/send-email', methods=['POST'])
def email_api():
    try:
        data = request.json

        # Extracting email parameters from the JSON payload
        sender_email = data['sender_email']
        receiver_email = data['receiver_email']
        cc_emails = data.get('cc_emails', [])
        bcc_emails = data.get('bcc_emails', [])
        subject = data['subject']
        message_body = data['message_body']
        # attachments = data.get('attachments', [])  # List of attachments

        # Extracting SMTP configuration
        smtp_config = {
            'server': data['smtp_config']['server'],
            'port': data['smtp_config']['port'],
            'username': data['smtp_config']['username'],
            'password': data['smtp_config']['password']
        }

        # Converting attachment content from base64 to bytes
        # for attachment in attachments:
        #     attachment['content'] = base64.b64decode(attachment['content'])

        # Call send_email with dynamic parameters
        send_email(
            sender_email=sender_email,
            receiver_email=receiver_email,
            cc_emails=cc_emails,
            bcc_emails=bcc_emails,
            subject=subject,
            message_body=message_body,
            # attachments=attachments,
            smtp_config=smtp_config
        )
        return jsonify({"status": "success", "message": "Email sent successfully"})
    except Exception as e:
        logging.error(f"Error: {e}")
        app.logger.error(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    

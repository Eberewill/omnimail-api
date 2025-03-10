import asyncio
from aiosmtpd.controller import Controller
from email import message_from_bytes
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models.base import Mailbox, EmailMessage

class OmniMailHandler:
    async def handle_DATA(self, server, session, envelope):
        print(f"Receiving message from: {envelope.mail_from}")
        print(f"Receiving message for: {envelope.rcpt_tos}")
        
        db = SessionLocal()
        try:
            # Extract basic email data
            msg = message_from_bytes(envelope.content)
            subject = msg.get('subject', '(No Subject)')
            sender = envelope.mail_from
            
            # Simple body extraction
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = msg.get_payload(decode=True).decode()

            # For each recipient, check if they have a mailbox on our platform
            for recipient in envelope.rcpt_tos:
                mailbox = db.query(Mailbox).filter(Mailbox.address == recipient.lower()).first()
                if mailbox:
                    new_email = EmailMessage(
                        mailbox_id=mailbox.id,
                        sender=sender,
                        subject=subject,
                        body=body,
                        raw_content=envelope.content.decode('utf-8', errors='ignore')
                    )
                    db.add(new_email)
            
            db.commit()
            print("Message successfully processed and saved.")
            return '250 Message accepted for delivery'
            
        except Exception as e:
            print(f"Error processing email: {e}")
            return '500 Error processing message'
        finally:
            db.close()

def start_smtp_server(host="0.0.0.0", port=2525):
    handler = OmniMailHandler()
    controller = Controller(handler, hostname=host, port=port)
    controller.start()
    print(f"SMTP Server started on {host}:{port}")
    return controller

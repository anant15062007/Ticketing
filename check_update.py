from sqlalchemy.orm import Session
from models import TicketReplyModel, UserRoleModel, TicketModel
from send_mail_of_update import sendUpdateMail
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ticketing_db")

engine = create_engine(
    DATABASE_URL,
    pool_size=20,        # Increase the base parking spaces
    max_overflow=30,     # Increase the waiting line
    pool_timeout=60      # Give tasks 60 seconds to wait in line before crashing
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def process_unsent_emails():
    """
    Scans the database for unsent emails and determines the action 
    based on the author's role.
    """

    db = SessionLocal()

    # 1. Fetch all replies where email_sent is explicitly False
    unsent_replies = db.query(TicketReplyModel).filter(TicketReplyModel.email_sent == False).all()

    if not unsent_replies:
        print("All emails have been sent. Nothing to process.")
        return

    for reply in unsent_replies:
        print(f"Checking Ticket ID #{reply.ticket_id} from {reply.author_email}...")

        # 2. Look up the author in the users table to determine their role
        author = db.query(UserRoleModel).filter(UserRoleModel.email == reply.author_email).first()
        parent_ticket = db.query(TicketModel).filter(TicketModel.id == reply.ticket_id).first()
        mailId = parent_ticket.creator_email

        # Safety check in case the user was deleted
        if not author:
            print(f"⚠️ Could not find role for {reply.author_email}. Skipping.")
            continue

        # 3. Route the logic based on the author's role
        if author.role == 'Owner' or author.role == 'Admin':
            sendUpdateMail(mailId, reply.ticket_id)
            
        elif author.role == 'User':
            mailId = parent_ticket.assigned_to
            sendUpdateMail(mailId, reply.ticket_id)

            # Do user-specific logic here (e.g., notify admins)
            
        else:
            print(f"❓ Unknown role '{author.role}' for {reply.author_email}")

        # 4. Once processed, mark it as sent so it isn't processed again
        reply.email_sent = True
        db.commit()
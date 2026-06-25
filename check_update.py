from sqlalchemy.orm import Session
from models import TicketReplyModel, UserRoleModel, TicketModel
from send_mail_of_update import sendUpdateMail, send_agent_invite
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
    Scans the database for unsent ticket replies and unsent agent invites,
    processing each and dispatching the appropriate emails.
    """

    db = SessionLocal()

    try:
        # ==========================================
        # PART 1: PROCESS UNSENT TICKET REPLIES
        # ==========================================
        unsent_replies = db.query(TicketReplyModel).filter(TicketReplyModel.email_sent == False).all()

        if not unsent_replies:
            print("No unsent replies to process.")
        else:
            for reply in unsent_replies:
                print(f"Checking Ticket ID #{reply.ticket_id} from {reply.author_email}...")

                # Look up the author in the users table to determine their role
                author = db.query(UserRoleModel).filter(UserRoleModel.email == reply.author_email).first()
                parent_ticket = db.query(TicketModel).filter(TicketModel.id == reply.ticket_id).first()
                
                # Safety check in case the user or ticket was deleted
                if not author or not parent_ticket:
                    print(f"⚠️ Missing author or ticket for reply ID {reply.id}. Skipping.")
                    continue

                # Route the logic based on the author's role
                if author.role == 'Owner' or author.role == 'Admin':
                    sendUpdateMail(parent_ticket.creator_email, reply.ticket_id)
                    
                elif author.role == 'User':
                    sendUpdateMail(parent_ticket.assigned_to, reply.ticket_id)
                    
                else:
                    print(f"❓ Unknown role '{author.role}' for {reply.author_email}")

                # Once processed, mark it as sent so it isn't processed again
                reply.email_sent = True


        # ==========================================
        # PART 2: PROCESS NEW ACCOUNTS (AGENTS & USERS)
        # ==========================================
        # Fetch ALL accounts where 'created' is False
        new_accounts = db.query(UserRoleModel).filter(UserRoleModel.created == False).all()

        if not new_accounts:
            print("No new accounts to process.")
        else:
            for account in new_accounts:
                
                # Check the role inside the loop
                if account.role == 'Admin' or account.role == 'Owner':
                    print(f"Sending invite to new agent: {account.email}...")
                    
                    send_agent_invite(account.email, account.hashed_password) 
                    account.created = True
                    
                elif account.role == 'User':
                    print(f"Silently verifying standard user: {account.email}...")
                    account.created = True
                else:
                    print(f"❓ Unknown role '{account.role}' for {account.email}. Skipping.")

        db.commit()

    finally:
        db.close()
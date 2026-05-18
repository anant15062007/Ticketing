import psycopg2
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/ticketing_db"
)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def get_issue_from_db(thread_id):

    conn = get_db_connection()
    cur = conn.cursor()
    
    query = "SELECT issue_number FROM tickets_schema.issue_mappings WHERE thread_id = %s;"
    cur.execute(query, (thread_id,))
    
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return result[0] if result else None

def find_threadID(thread_id):

    conn = get_db_connection()
    cur = conn.cursor()
    
    query = "SELECT EXISTS(SELECT 1 FROM tickets_schema.issue_mappings WHERE thread_id = %s);"
    
    cur.execute(query, (thread_id,))
    exists = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return exists


def find_messageID(message_id):

    conn = get_db_connection()
    cur = conn.cursor()
    
    query = "SELECT EXISTS(SELECT 1 FROM tickets_schema.issue_mappings WHERE message_id = %s);"
    
    cur.execute(query, (message_id,))
    exists = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return exists
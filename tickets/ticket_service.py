from database.db import get_connection


def create_ticket(user_id, document_id, message):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tickets (user_id, document_id, message, status)
        VALUES (?, ?, ?, 'open')
    """, (user_id, document_id, message))

    conn.commit()
    conn.close()


def get_user_tickets(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM tickets
        WHERE user_id=?
        ORDER BY created_at DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_staff_tickets():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.*, d.title as doc_title, u.full_name as user_name
        FROM tickets t
        JOIN documents d ON t.document_id = d.id
        JOIN users u ON t.user_id = u.id
        WHERE t.status='open'
        ORDER BY t.created_at ASC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def reply_ticket(ticket_id, staff_id, response):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tickets
        SET staff_id=?, response=?, status='answered'
        WHERE id=?
    """, (staff_id, response, ticket_id))

    conn.commit()
    conn.close()

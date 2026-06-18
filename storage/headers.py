from utils.id_generator import generate_header
from database.db import get_connection

def create_header(document_id):
    header = generate_header()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE documents SET header_code = ? WHERE id = ?",
        (header, document_id)
    )

    conn.commit()
    conn.close()
    return header

def get_header(document_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT header_code FROM documents WHERE id = ?",
        (document_id,)
    )

    row = cursor.fetchone()
    conn.close()

    return row["header_code"] if row else None

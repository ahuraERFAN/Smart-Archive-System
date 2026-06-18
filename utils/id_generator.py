import uuid
import datetime
import random
import string


def generate_header():
    date_part = datetime.datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"HDR-{date_part}-{random_part}"


def generate_archive_key():
    key = uuid.uuid4().hex.upper()
    return f"KEY-{key[:16]}"


def generate_ticket_id():
    date_part = datetime.datetime.now().strftime("%Y%m%d")
    rand = ''.join(random.choices(string.digits, k=5))
    return f"TCK-{date_part}-{rand}"

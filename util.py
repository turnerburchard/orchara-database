import os
from datetime import date
import json

import psycopg2
from dotenv import load_dotenv


def format_date(date_parts):
    """
    Converts a list of date parts [year, month, day] into a YYYY-MM-DD string.
    Returns None if conversion fails.
    """
    if date_parts and len(date_parts) >= 3:
        try:
            return date(date_parts[0], date_parts[1], date_parts[2]).isoformat()
        except Exception:
            return None
    return None


def safe_convert(value):
    """
    Safely converts the input value into a JSON-serializable form.
    If the value is None, returns None.
    If the value is already a dict, list, int, float, or str, it is returned as is.
    Otherwise, attempts to serialize and then deserialize the value; if that fails,
    it returns the string representation of the value.
    """
    if value is None:
        return None
    if isinstance(value, (dict, list, int, float, str, bool)):
        return value
    try:
        # Try to ensure the value is JSON-serializable
        return json.loads(json.dumps(value))
    except (TypeError, ValueError):
        return str(value)


def get_connection():
    """
    Establishes a PostgreSQL connection using credentials from the .env file.
    """
    load_dotenv()  # Ensure .env variables are loaded
    return psycopg2.connect(
        dbname=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        host=os.environ.get('DB_HOST'),
        port=os.environ.get('DB_PORT')
    )

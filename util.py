from datetime import date

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

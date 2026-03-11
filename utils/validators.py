import re


def parse_phone_numbers(raw_input: str) -> list[str]:
    """
    Parse phone numbers from free-form text input.
    Accepts comma-separated, newline-separated, or space-separated numbers.
    Strips whitespace and filters out blanks.
    """
    numbers = re.split(r"[,\n\s]+", raw_input.strip())
    return [n.strip() for n in numbers if n.strip()]


def validate_phone_number(phone: str) -> str | None:
    """Return an error message if the phone number looks invalid, else None."""
    cleaned = phone.strip()
    if not cleaned:
        return "Phone number cannot be empty."
    if not re.match(r"^[\d+\-() ]{5,20}$", cleaned):
        return f"'{cleaned}' does not look like a valid phone number."
    return None

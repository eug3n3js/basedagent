import secrets
import string


def generate_unique_code(length: int = 8) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_unique_digit_code(length: int = 6) -> str:
    return ''.join(secrets.choice(string.digits) for _ in range(length))

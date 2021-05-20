from django.core.management.utils import get_random_secret_key


def generate_secret_key(out_file: str):
    """Writes a secrect key given file.

    Args:
        out_file (str): Path to store key to.
    """
    secret_key = get_random_secret_key()
    with open(out_file, "w") as of:
        of.writelines(f"SECRET_KEY = '{secret_key}'")

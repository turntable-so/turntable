import argparse
import base64
import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()


def encrypt_secret(secret: str):
    cipher = Fernet(os.getenv("ENCRYPTION_KEY"))
    encrypted_secret = cipher.encrypt(secret.encode("utf-8"))
    encoded_encrypted_data = base64.urlsafe_b64encode(encrypted_secret).decode("utf-8")
    return encoded_encrypted_data


def main():
    parser = argparse.ArgumentParser(description="Encrypt a secret")
    parser.add_argument(
        "--secret", type=str, help="The secret to encrypt. Pass in single quotes."
    )
    args = parser.parse_args()
    print(encrypt_secret(args.secret))

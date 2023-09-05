import os
import string
import random

JWT_KEY_FILE = '.JWT_KEY'


def generate_random_password(length):
    """Generate a random password of the given length."""
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))


def get_JWT_secret_KEY():
    if os.path.exists(JWT_KEY_FILE):
        with open(JWT_KEY_FILE, 'r') as f:
            jwt_key = f.read().strip()
    else:
        jwt_key = generate_random_password(18)
        with open(JWT_KEY_FILE, 'w') as f:
            f.write(jwt_key)

    return jwt_key

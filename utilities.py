import hashlib


def hash_password(password):
    hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

    return hashed_password

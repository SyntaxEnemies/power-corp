from bcrypt import gensalt, hashpw, checkpw

def get_hash(plain: str) -> str:
    salt = gensalt()
    return hashpw(plain.encode('utf-8'), salt).decode('utf-8')

def check_hash(plain: str, hash: str) -> bool:
    return checkpw(plain.encode('utf-8'), hash.encode('utf-8'))

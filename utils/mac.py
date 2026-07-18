from utils.hash import SHA1
from utils.oracles import global_key

def secret_prefix_mac(message: bytes) -> str:
    data = global_key + message
    sha1 = SHA1()
    return sha1.compute_hash(data)

def verify_secret_prefix_mac(message: bytes, tag: str) -> bool:
    return secret_prefix_mac(message) == tag
from utils.crypto import aes_ctr
import base64

encrypted_text = "L77na/nrFsKvynd6HzOoG7GHTLXsTVu9qvY/2syLXzhPweyyMTJULu/6/kXX0KSvoOLSFQ=="
key = b"YELLOW SUBMARINE"

def solve():
    encrypted_bytes = base64.b64decode(encrypted_text)
    print(aes_ctr(encrypted_bytes, key).decode('utf-8', errors="replace"))


if __name__ == "__main__":
    solve()
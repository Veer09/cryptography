
from utils.xor import find_key
import secrets
from utils.crypto import aes_ctr
import base64

def solve():
    key = secrets.token_bytes(16)
    ciphertexts = []
    with open("challenges/set3/4.txt", "r") as f:
        for line in f:
            line = line.strip()
            decoded_bytes = base64.b64decode(line)
            cipher = aes_ctr(decoded_bytes, key)
            ciphertexts.append(cipher)
    repeated_key = [bytes(column) for column in zip(*ciphertexts)]
    key_stream = bytearray()
    for block in repeated_key:
        _, _, key_byte = find_key(block)
        key_stream.append(key_byte)

    for ciphertext in ciphertexts:
        target_chunk = ciphertext[:len(key_stream)]
        plaintext = bytes(a ^ b for a, b in zip(target_chunk, key_stream))
        print(plaintext.decode('ascii', errors='replace')) 
        
if __name__ == "__main__":
    solve()
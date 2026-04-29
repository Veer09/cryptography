
from utils import bytes_to_base64
from utils import encrypt_aes_cbc
from utils import remove_pkcs7_padding
from utils import decrypt_aes_cbc
import base64
key = "YELLOW SUBMARINE"
iv = bytes([0]) * 16

def solve():
    with open("challenges/set2/2.txt", "r") as f:
        ciphertext = base64.b64decode(f.read())
        print(bytes_to_base64(encrypt_aes_cbc(remove_pkcs7_padding(decrypt_aes_cbc(ciphertext, key.encode('utf-8'), iv)), key.encode('utf-8'), iv)))

if __name__ == "__main__":
    solve()
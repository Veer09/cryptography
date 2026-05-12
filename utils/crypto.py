# pyrefly: ignore [missing-import]
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# pyrefly: ignore [missing-import]
from cryptography.hazmat.backends import default_backend
from utils.xor import perform_xor



def pkcs7_padding(plaintext: bytes, block_size: int) -> bytes:
    padds = block_size - (len(plaintext) % block_size)
    padding = bytes([padds]) * padds
    return plaintext + padding


def remove_pkcs7_padding(plaintext: bytes) -> bytes:
    padds = plaintext[-1]
    if padds == 0 or padds > 16:
        raise ValueError("Invalid Padding Length!!")
    if plaintext[-padds:] != bytes([padds]) * padds:
        raise ValueError("Inavlid PKCS#7 Padding!!!")
    return plaintext[:-padds]


def decrypt_aes_ecb(ciphertext: bytes, key: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()


def encrypt_aes_ecb(plaintext: bytes, key: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(plaintext) + encryptor.finalize()


def decrypt_aes_cbc(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    plaintext = bytearray()
    previous = iv
    for i in range(0, len(ciphertext), 16):
        block = ciphertext[i : i + 16]
        pt = decrypt_aes_ecb(block, key)
        plaintext.extend(perform_xor(pt, previous))
        previous = block
    return bytes(plaintext)


def encrypt_aes_cbc(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    padded_text = pkcs7_padding(plaintext, 16)
    ciphertext = bytearray()
    previous = iv
    for i in range(0, len(padded_text), 16):
        block = padded_text[i : i + 16]
        ct = encrypt_aes_ecb(perform_xor(block, previous), key)
        previous = ct
        ciphertext.extend(ct)
    return bytes(ciphertext)


def detect_ecb(ciphertext: bytes) -> bool:
    blocks = {}
    for i in range(0, len(ciphertext), 16):
        key = ciphertext[i : i + 16]
        blocks[key] = blocks.get(key, 0) + 1
    for key in blocks:
        if blocks[key] > 1:
            return True
    return False


def generate_keystream(nonce: bytes, counter: bytes, key: bytes) -> bytes:
    iv = nonce + counter
    return encrypt_aes_ecb(iv, key)


def aes_ctr(text: bytes, key: bytes) -> bytes:
    nonce = 0
    blocks = -(len(text) // -16)
    cipher = b""
    for i in range(blocks):
        ks = generate_keystream(
            nonce.to_bytes(8, byteorder="little"),
            i.to_bytes(8, byteorder="little"),
            key,
        )
        block_text = text[i * 16 : (i + 1) * 16]
        cipher += perform_xor(ks[: len(block_text)], block_text)
    return cipher

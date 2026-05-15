from utils.crypto import encryption_mt19937
import secrets
from utils.crypto import MT19937
import secrets
import random
import base64
import time
from utils.crypto import (
    encrypt_aes_ecb,
    encrypt_aes_cbc,
    decrypt_aes_ecb,
    decrypt_aes_cbc,
    pkcs7_padding,
    remove_pkcs7_padding,
)
from utils.xor import perform_xor

global_key = secrets.token_bytes(16)
user_profile_key = secrets.token_bytes(16)
random_length = random.randint(8, 64)
random_prefix = secrets.token_bytes(random_length)
random_iv = secrets.token_bytes(16)


def encryption_oracle(plaintext: bytes) -> bytes:
    key = secrets.token_bytes(16)
    prefix = random.randint(5, 10)
    suffix = random.randint(5, 10)
    padded_text = secrets.token_bytes(prefix) + plaintext + secrets.token_bytes(suffix)
    decider = random.randint(0, 1)
    print(decider)
    if decider:
        return encrypt_aes_ecb(pkcs7_padding(padded_text, 16), key)
    else:
        iv = secrets.token_bytes(16)
        return encrypt_aes_cbc(padded_text, key, iv)


def new_oracle(plaintext: bytes) -> bytes:
    unknown_text = "Um9sbGluJyBpbiBteSA1LjAKV2l0aCBteSByYWctdG9wIGRvd24gc28gbXkgaGFpciBjYW4gYmxvdwpUaGUgZ2lybGllcyBvbiBzdGFuZGJ5IHdhdmluZyBqdXN0IHRvIHNheSBoaQpEaWQgeW91IHN0b3A/IE5vLCBJIGp1c3QgZHJvdmUgYnkK"
    unknown_bytes = base64.b64decode(unknown_text)
    padded_text = pkcs7_padding(plaintext + unknown_bytes, 16)
    return encrypt_aes_ecb(padded_text, global_key)


def kv_parsing(kv_string: str) -> dict[str, any]:
    kv_pairs = kv_string.split("&")
    kv = {}
    for kv_pair in kv_pairs:
        kv_value = kv_pair.split("=")
        if len(kv_value) == 2:
            kv[kv_value[0]] = kv_value[1]
    return kv


def profile_for(email: str) -> str:
    email_part = email.split("&")[0]
    email_stripped = email_part.split("=")[0]
    user = {"email": email_stripped, "uid": 10, "role": "user"}
    encoded_user = ""
    for key in user:
        encoded_user = encoded_user + key + "=" + str(user[key]) + "&"
    return encoded_user[:-1]


def encrypt_profile(email: str) -> bytes:
    encoded_profile = profile_for(email)
    return encrypt_aes_ecb(
        pkcs7_padding(encoded_profile.encode("utf-8"), 16), user_profile_key
    )


def decrypt_profile(ciphertext: bytes) -> dict[str, any]:
    decrypted_profile = remove_pkcs7_padding(
        decrypt_aes_ecb(ciphertext, user_profile_key)
    )
    return kv_parsing(decrypted_profile.decode("utf-8"))


def new_oracle2(plaintext: bytes) -> bytes:
    unknown_text = "Um9sbGluJyBpbiBteSA1LjAKV2l0aCBteSByYWctdG9wIGRvd24gc28gbXkgaGFpciBjYW4gYmxvdwpUaGUgZ2lybGllcyBvbiBzdGFuZGJ5IHdhdmluZyBqdXN0IHRvIHNheSBoaQpEaWQgeW91IHN0b3A/IE5vLCBJIGp1c3QgZHJvdmUgYnkK"
    unknown_bytes = base64.b64decode(unknown_text)
    padded_text = pkcs7_padding(random_prefix + plaintext + unknown_bytes, 16)
    return encrypt_aes_ecb(padded_text, global_key)


def encryption_cbc_bitflip(plaintext: bytes) -> bytes:
    prefix = b"comment1=cooking%20MCs;userdata="
    suffix = b";comment2=%20like%20a%20pound%20of%20bacon"
    plaintext_stripped = plaintext.split(b";")[0].split(b"=")[0]
    cipher = encrypt_aes_cbc(
        prefix + plaintext_stripped + suffix, global_key, random_iv
    )
    return cipher


def decryption_cbc_bitflip(ciphertext: bytes) -> bool:
    plaintext = decrypt_aes_cbc(ciphertext, global_key, random_iv)
    if plaintext.find(b";admin=true;") == -1:
        return False
    return True


def encryption_padding_oracle() -> tuple[bytes, bytes]:
    plaintexts = [
        "MDAwMDAwTm93IHRoYXQgdGhlIHBhcnR5IGlzIGp1bXBpbmc=",
        "MDAwMDAxV2l0aCB0aGUgYmFzcyBraWNrZWQgaW4gYW5kIHRoZSBWZWdhJ3MgYXJlIHB1bXBpbic=",
        "MDAwMDAyUXVpY2sgdG8gdGhlIHBvaW50LCB0byB0aGUgcG9pbnQsIG5vIGZha2luZw==",
        "MDAwMDAzQ29va2luZyBNQydzIGxpa2UgYSBwb3VuZCBvZiBiYWNvbg==",
        "MDAwMDA0QnVybmluZyAnZW0sIGlmIHlvdSBhaW4ndCBxdWljayBhbmQgbmltYmxl",
        "MDAwMDA1SSBnbyBjcmF6eSB3aGVuIEkgaGVhciBhIGN5bWJhbA==",
        "MDAwMDA2QW5kIGEgaGlnaCBoYXQgd2l0aCBhIHNvdXBlZCB1cCB0ZW1wbw==",
        "MDAwMDA3SSdtIG9uIGEgcm9sbCwgaXQncyB0aW1lIHRvIGdvIHNvbG8=",
        "MDAwMDA4b2xsaW4nIGluIG15IGZpdmUgcG9pbnQgb2g=",
        "MDAwMDA5aXRoIG15IHJhZy10b3AgZG93biBzbyBteSBoYWlyIGNhbiBibG93",
    ]
    plaintext = base64.b64decode(random.choice(plaintexts))
    iv = secrets.token_bytes(16)
    return iv, encrypt_aes_cbc(plaintext, global_key, iv)


def padding_oracle(iv: bytes, ciphertext: bytes) -> bool:
    plaintext = decrypt_aes_cbc(ciphertext, global_key, iv)
    try:
        remove_pkcs7_padding(plaintext)
        return True
    except ValueError:
        return False

def random_oracle() -> tuple[int, int]:
    current_timestamp = int(time.time())
    first_stop = random.randint(40, 1000)
    seed_timestamp = current_timestamp + first_stop
    print("Seeded Timestamp: " + str(seed_timestamp))
    mt19937 = MT19937(seed_timestamp)
    random_num = mt19937.generate_number()
    second_stop = random.randint(40, 1000)
    return random_num, seed_timestamp + second_stop

def stream_cipher_oracle(plaintext: bytes) -> bytes:
    key = int(secrets.randbits(16))
    print(key)
    random_len = random.randint(5, 30)
    random_prefix = secrets.token_bytes(random_len)
    cipher = encryption_mt19937(random_prefix+plaintext, key)
    return cipher

def get_password_token() -> int:
    timestamp = int(time.time())
    generator = MT19937(timestamp)
    return generator.generate_number()

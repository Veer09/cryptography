import secrets
import random
import secrets
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def hex_to_bytes(hex: str) -> bytes:
    if len(hex) % 2 != 0:
        raise ValueError("Hex string must have an even number of characters to convert to bytes")
    
    result = bytearray()
    for i in range(0, len(hex), 2):
        byte = int(hex[i:i+2], 16)
        result.append(byte)
    return bytes(result)

def bytes_to_base64(b: bytes) -> str:
    base64_map = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    result = ""
    for i in range(0, len(b), 3):
        b1 = b[i]
        b2 = b[i+1] if i+1 < len(b) else 0
        b3 = b[i+2] if i+2 < len(b) else 0
        c1 = b1 >> 2
        c2 = (b1 & 0x03) << 4 | b2 >> 4
        c3 = (b2 & 0x0F) << 2 | b3 >> 6
        c4 = b3 & 0x3F
        result += base64_map[c1] + base64_map[c2]
        result += base64_map[c3] if i+1 < len(b) else "="
        result += base64_map[c4] if i+2 < len(b) else "="
    return result      

def perform_xor(b1: bytes, b2: bytes) -> bytes:
    if len(b1) != len(b2):
        raise ValueError("Byte strings must have the same length to perform XOR")
    
    result = bytearray()
    for i in range(len(b1)):
        result.append(b1[i] ^ b2[i])
    return bytes(result) 

def single_byte_xor(b: bytes, key: int) -> bytes:
    result = bytearray()
    for i in range(len(b)):
        result_byte = b[i] ^ key
        result.append(result_byte)
    return bytes(result)

def repeated_key_xor(b: bytes, key: bytes) -> bytes:
    result = bytearray()
    for i in range(len(b)):
        result_byte = b[i] ^ key[i % len(key)]
        result.append(result_byte)
    return bytes(result)

def score_text(text: bytes) -> int:
    score = 0
    for b in text:
        char = chr(b).lower()
        if char in "etaoin":
            score += 5
        elif char in "shrdlu":
            score += 3
        elif char == " ":
            score += 10
        elif 32 <= b <= 126:
            score += 1
        else:
            score -= 20
    return score

def calculate_hamming_distance(b1: bytes, b2:bytes):
    if len(b1) != len(b2):
        raise ValueError("Byte strings must have the same length to calculate Hamming Distance!!")
    return sum(byte.bit_count() for byte in perform_xor(b1, b2))

def find_key(b: bytes) -> tuple[int, bytes, int]:
    best_score = float('-inf')
    best_result = b""
    enc_key = 0
    for i in range(256):
        result = single_byte_xor(b, i)
        score = score_text(result)
        if score > best_score:
            best_score = score
            best_result = result
            enc_key = i
    return best_score, best_result, enc_key

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
        block = ciphertext[i:i+16]
        pt = decrypt_aes_ecb(block, key)
        plaintext.extend(perform_xor(pt, previous))
        previous = block
    return bytes(plaintext)

def encrypt_aes_cbc(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    padded_text = pkcs7_padding(plaintext, 16)
    ciphertext = bytearray()
    previous = iv
    for i in range(0, len(padded_text), 16):
        block = padded_text[i:i+16]
        ct = encrypt_aes_ecb(perform_xor(block, previous), key)
        previous = ct
        ciphertext.extend(ct)
    return bytes(ciphertext)

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
    
def detect_ecb(ciphertext: bytes) -> bool:
    blocks = {}
    for i in range(0, len(ciphertext), 16):
        key = ciphertext[i:i+16]
        blocks[key] = blocks.get(key, 0) + 1
    for key in blocks:
        if blocks[key] > 1:
            return True
    return False
    
global_key = secrets.token_bytes(16)

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
    user = {
        "email": email_stripped,
        "uid": 10,
        "role": "user"
    }
    encoded_user = ""
    for key in user:
        encoded_user = encoded_user + key + "=" + str(user[key]) + "&"
    return encoded_user[:-1] 


user_profile_key = secrets.token_bytes(16)

def encrypt_profile(email: str) -> bytes:
    encoded_profile = profile_for(email)
    return encrypt_aes_ecb(pkcs7_padding(encoded_profile.encode('utf-8'), 16), user_profile_key)

def decrypt_profile(ciphertext: bytes) -> dict[str, any]:
    decrypted_profile = remove_pkcs7_padding(decrypt_aes_ecb(ciphertext, user_profile_key))
    return kv_parsing(decrypted_profile.decode('utf-8'))

random_length = random.randint(8, 64)
random_prefix = secrets.token_bytes(random_length)

def new_oracle2(plaintext: bytes) -> bytes:
    unknown_text = "Um9sbGluJyBpbiBteSA1LjAKV2l0aCBteSByYWctdG9wIGRvd24gc28gbXkgaGFpciBjYW4gYmxvdwpUaGUgZ2lybGllcyBvbiBzdGFuZGJ5IHdhdmluZyBqdXN0IHRvIHNheSBoaQpEaWQgeW91IHN0b3A/IE5vLCBJIGp1c3QgZHJvdmUgYnkK"
    unknown_bytes = base64.b64decode(unknown_text)
    padded_text = pkcs7_padding(random_prefix + plaintext + unknown_bytes, 16)
    return encrypt_aes_ecb(padded_text, global_key)

random_iv = secrets.token_bytes(16)

def encryption_cbc_bitflip(plaintext: bytes) -> bytes:
    prefix = b"comment1=cooking%20MCs;userdata="
    suffix = b";comment2=%20like%20a%20pound%20of%20bacon"

    plaintext_stripped = plaintext.split(b";")[0].split(b"=")[0]
    cipher = encrypt_aes_cbc(prefix + plaintext_stripped + suffix, global_key, random_iv)
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
    "MDAwMDA5aXRoIG15IHJhZy10b3AgZG93biBzbyBteSBoYWlyIGNhbiBibG93"
    ]
    plaintext = base64.b64decode(random.choice(plaintexts)) 
    iv = secrets.token_bytes(16)
    return iv, encrypt_aes_cbc(plaintext, global_key, iv)

def padding_oracle(iv: bytes, ciphertext: bytes) -> bool:
    plaintext = decrypt_aes_cbc(ciphertext, global_key, iv)
    try:
        removed_padded_text = remove_pkcs7_padding(plaintext)
        return True
    except ValueError:
        return False



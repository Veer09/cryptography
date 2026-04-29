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
    return plaintext[:-padds]
    
def hex_to_bytes(hex: str) -> bytes:
    if len(hex) % 2 != 0:
        raise ValueError("Hex string must have an even number of characters to convert to bytes")
    
    result = bytearray()
    for i in range(0, len(hex), 2):
        byte = int(hex[i:i+2], 16)
        result.append(byte)

    return bytes(result)

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
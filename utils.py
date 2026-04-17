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
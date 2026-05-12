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

def calculate_hamming_distance(b1: bytes, b2: bytes):
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


def interactive_crib_drag(ciphertexts: list[bytes]):
    print("Welcome to the Crib Dragging Tool!")
    print("Press Ctrl+C to exit at any time.\n")
    
    while True:
        try:
            print("=" * 60)

            target_line = int(input("1. Which line # do you want to guess on? (0 to 39): "))
            offset = int(input("2. At what position (index) does your guess start?: "))
            guess = input("3. Enter your text guess (e.g., ' the ', 'ing'): ").encode('ascii')

            target_cipher = ciphertexts[target_line]
            target_chunk = target_cipher[offset : offset + len(guess)]
            
            derived_keystream = perform_xor(target_chunk, guess)

            print(f"\n--- Results for guess '{guess.decode()}' at index {offset} ---")

            for i, ct in enumerate(ciphertexts):
                if offset >= len(ct):
                    continue 

                ct_chunk = ct[offset : offset + len(derived_keystream)]
                
                decrypted_chunk = perform_xor(ct_chunk, derived_keystream)
                
                safe_text = "".join(chr(b) if 32 <= b <= 126 else "." for b in decrypted_chunk)
                
                if i == target_line:
                    print(f"Line {i:02} (Target): -> {safe_text} <-")
                else:
                    print(f"Line {i:02}:         {safe_text}")
                    
        except ValueError:
            print("\n[!] Invalid input. Please enter numbers for line/offset.")
        except IndexError:
            print("\n[!] That offset is too long for the target line.")
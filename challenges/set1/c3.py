from utils import hex_to_bytes, perform_xor, score_text

msg = "1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736"

def solve():
    hex_msg = hex_to_bytes(msg)
    best_score = -1
    best_result = b""
    enc_key = 0
    for i in range(256):
        key = bytes([i] * len(hex_msg))
        result = perform_xor(hex_msg, key)
        score = score_text(result)
        if score > best_score:
            best_score = score
            best_result = result
            enc_key = i
    print(f"Score: {best_score}, Result: {best_result}, Key: {enc_key}")

if __name__ == "__main__":
    solve()

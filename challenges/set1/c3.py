from utils import hex_to_bytes, find_key

msg = "1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736"

def solve():
    bytes_msg = hex_to_bytes(msg)
    best_score, best_result, enc_key = find_key(bytes_msg)
    print(f"Decrypted Message: {best_result}, Key: {chr(enc_key)}, Score: {best_score}")

if __name__ == "__main__":
    solve()

from utils import hex_to_bytes, perform_xor, score_text

def solve():
    best_score = -1
    best_result = b""
    msg_string = ""
    enc_key = 0
    with open("./challenges/set1/4.txt", "r") as f:
        for line in f:
            line = line.strip()
            msg = hex_to_bytes(line)
            for i in range(256):
                key = bytes([i] * len(msg))
                result = perform_xor(msg, key)
                score = score_text(result)
                if score > best_score:
                    best_score = score
                    best_result = result
                    msg_string = line
                    enc_key = i
    print(f"Message: {msg_string}, Score: {best_score}, Result: {best_result}, Key: {enc_key}")

if __name__ == "__main__":
    solve()
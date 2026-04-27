import utils
import base64

key = "YELLOW SUBMARINE"

def solve():
    with open("challenges/set1/7.txt", "r") as f:
        data = base64.b64decode(f.read())
        decrypted_text = utils.decrypt_aes_ecb(data, key.encode('utf-8'))
        print(f"Decrypted Text:\n{decrypted_text.decode('utf-8', errors='replace')}")

if __name__ == "__main__":
    solve()
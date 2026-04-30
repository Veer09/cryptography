from utils import encryption_oracle
from utils import detect_ecb
def solve():
    plaintext = bytes([65]) * 64
    print(detect_ecb(encryption_oracle(plaintext)))

if __name__ == "__main__":
    solve()
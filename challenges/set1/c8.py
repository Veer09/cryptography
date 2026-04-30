from utils import detect_ecb
from utils import hex_to_bytes

def solve():
    with open("challenges/set1/8.txt", "r") as f:
        ecbs = []
        for line in f:
            line = line.strip()
            msg = hex_to_bytes(line)
            if detect_ecb(msg):
                ecbs.append(msg)
        
        for ecb in ecbs:
            print(ecb)


if __name__ == "__main__":
    solve()
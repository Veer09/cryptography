from utils import hex_to_bytes

def solve():
    with open("challenges/set1/8.txt", "r") as f:
        ecbs = []
        for line in f:
            line = line.strip()
            blocks = {}
            msg = hex_to_bytes(line)
            for i in range(0, len(msg), 16):
                key = msg[i:i+16]
                blocks[key] = blocks.get(key, 0) + 1

            for key in blocks:
                if blocks[key] > 1:
                    ecbs.append(line)
                    break
        
        for ecb in ecbs:
            print(ecb)


if __name__ == "__main__":
    solve()
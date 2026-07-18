from utils.mac import verify_secret_prefix_mac
from utils.mac import secret_prefix_mac
from utils.hash import SHA1

def solve():
    with open("challenges/set4/1.txt", "r") as f:
        message = f.read()
        message_bytes = message.encode("utf-8")
        tag = secret_prefix_mac(message_bytes)
        print(verify_secret_prefix_mac(message_bytes, tag))            
        
if __name__ == "__main__":
    solve()
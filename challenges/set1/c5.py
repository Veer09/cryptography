
from utils import repeated_key_xor

msg = (
    "Burning 'em, if you ain't quick and nimble\n"
    "I go crazy when I hear a cymbal"
)

key = "ICE"

def solve():
    msg_bytes = msg.encode('utf-8')
    key_bytes = key.encode('utf-8')
    print(repeated_key_xor(msg_bytes, key_bytes).hex())

if __name__ == "__main__":
    solve()


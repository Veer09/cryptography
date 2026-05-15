from utils.oracles import get_password_token
import time
from utils.xor import perform_xor
from utils.crypto import MT19937
from utils.oracles import stream_cipher_oracle

def token_checker(token: int) -> bool:
    ts = int(time.time())
    for i in range(2000):
        seeded_ts = ts - i
        generator = MT19937(seeded_ts)
        if generator.generate_number() == token:
            return True
    return False

def solve():
    # Part 1
    plaintext = bytes([65]) * 30
    cipher = stream_cipher_oracle(plaintext)
    known_ks = perform_xor(plaintext, cipher[-30:])
    for i in range(65536):
        generator = MT19937(i)
        random_arr_bytes = bytearray()
        for j in range(-(-len(cipher) // 4)):
            ran_bytes = generator.generate_number().to_bytes(4, "little")
            random_arr_bytes.extend(ran_bytes)
        random_arr_bytes = random_arr_bytes[:len(cipher)]
        if known_ks == random_arr_bytes[-30:]:
            print("Seed is: " + str(i))
            break

    # Part 2
    token = get_password_token()
    print(token_checker(token))

    
if __name__ == "__main__":
    solve()

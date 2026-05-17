
from utils import bytes_to_base64
from utils.xor import perform_xor
from utils.oracles import ctr_edit
from utils.oracles import ctr_oracle
import base64
def solve():
    with open("challenges/set4/1.txt", "r") as f:
        data = f.read()
        data_bytes = base64.b64decode(data)
        ciphertext = ctr_oracle(data_bytes)
        plaintext = bytes([65]) * len(ciphertext)
        modified_cipher = ctr_edit(ciphertext, 0, plaintext)
        keystream = perform_xor(modified_cipher, plaintext)
        original_plaintext = perform_xor(keystream, ciphertext)
        print(bytes_to_base64(original_plaintext))

            


if __name__ == "__main__":
    solve()
from utils import perform_xor
from utils.oracles import decryption_cbc_iv
from utils.oracles import encryption_cbc_iv


def solve():
    plaintext = bytes([130]) * 32
    ciphertext = encryption_cbc_iv(plaintext)
    modified_ciphertext = (
        ciphertext[:16] + bytes([0]) * 16 + ciphertext[:16] + ciphertext[48:]
    )
    try:
        print(decryption_cbc_iv(modified_ciphertext))
    except ValueError as e:
        text = e.args[0]
        first_block = text[:16]
        third_block = text[32:48]
        print(perform_xor(first_block, third_block))


if __name__ == "__main__":
    solve()

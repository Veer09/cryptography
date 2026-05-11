from utils import remove_pkcs7_padding
from utils import perform_xor
from utils import encryption_padding_oracle
from utils import padding_oracle


def solve():
    iv, cipher_only = encryption_padding_oracle()
    cipher_iv = iv + cipher_only
    plaintext = bytearray()
    iterations = len(cipher_iv) // 16
    for k in range(iterations-1):
        selected_cipher = bytearray(cipher_iv[k*16:(k+2)*16])
        is_first = True
        block = bytearray()
        last_padding = 1
        for j in range(16):
            for i in range(256):
                cipher_arr = bytearray(selected_cipher)
                cipher_arr[15 - j] = i
                if padding_oracle(iv, bytes(cipher_arr)):
                    if is_first:
                        cipher_arr[15 - j - 1] ^= 1
                        if not padding_oracle(iv, bytes(cipher_arr)):
                            continue
                        else:
                            is_first = False
                    last_byte = selected_cipher[15 - j] ^ i ^ last_padding
                    block.append(last_byte)
                    selected_cipher[15 - j] = i
                    for m in range(j + 1):
                        selected_cipher[15 - m] ^= last_padding ^ (last_padding + 1)
                    last_padding += 1
                    break
        block.reverse()
        plaintext.extend(block)
    print(remove_pkcs7_padding(bytes(plaintext)).decode('utf-8'))
    
if __name__ == "__main__":
    solve()

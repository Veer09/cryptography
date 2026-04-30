from utils import encryption_oracle
from utils import detect_ecb
from utils import new_oracle

def solve():
    i = 1
    blocksize = 0
    prev_len = 0
    while True:
        text = bytes([65]) * i
        i = i + 1
        cipher = new_oracle(text)
        if prev_len != 0 and prev_len != len(cipher):
            blocksize = len(cipher) - prev_len
            break
        if prev_len == 0:
            prev_len = len(cipher)
    
    plaintext = bytes([65]) * 64
    is_ecb = detect_ecb(new_oracle(plaintext))
    if is_ecb:
        iteration = 1 
        byte_no = 0
        test_bytes = bytes([65]) * (blocksize - 1)
        secret_msg = bytearray(test_bytes)
        while True:
            cipher = new_oracle(test_bytes[:(blocksize - (byte_no % blocksize))-1])
            cipher_map = {}
            for i in range(256):
                trial_byte = bytes([i])
                crafted_msg = secret_msg[-(blocksize-1):] + trial_byte
                ciphertext = new_oracle(crafted_msg)
                cipher_map[ciphertext[0:(blocksize)]] = trial_byte
            target = cipher[((iteration-1)*(blocksize)):(iteration)*(blocksize)]

            if target not in cipher_map:
                break

            if target in cipher_map:
                secret_msg.append(cipher_map[target][0]) 
                byte_no = byte_no + 1

            if byte_no % blocksize == 0:
                iteration = iteration + 1

        print(bytes(secret_msg[(blocksize-1):-1]).decode('utf-8'))
                        
if __name__ == "__main__":
    solve()
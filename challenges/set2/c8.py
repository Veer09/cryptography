from utils import perform_xor
from utils import encryption_cbc_bitflip
from utils import decryption_cbc_bitflip

def solve():
    # Selecting text such that blit-flip works well and also bypass encryption 
    temperedtext = b":admin<true:"
    ciphertext = encryption_cbc_bitflip(temperedtext)
    ciphertext_arr = bytearray(ciphertext)
    # Bytes which needs to be changed
    modification_bytes = [0, 6, 11]
    xor_byte = bytes([1])
    for i in modification_bytes:
        ciphertext_arr[16+i] = perform_xor(xor_byte, [ciphertext_arr[16+i]])[0]
    # Block-2 will be decrypted with random text while Block-3 has ;admin=true;
    print(decryption_cbc_bitflip(ciphertext_arr))

    
if __name__ == "__main__":
    solve()
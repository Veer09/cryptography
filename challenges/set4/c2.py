from utils.xor import perform_xor
from utils.oracles import encryption_ctr_bitflip
from utils.oracles import decryption_ctr_bitflip

def solve():
    temperedtext = b":admin<true:"
    ciphertext = encryption_ctr_bitflip(temperedtext)
    ciphertext_arr = bytearray(ciphertext)
    modification_bytes = [0, 6, 11]
    xor_byte = bytes([1])
    for i in modification_bytes:
        ciphertext_arr[32+i] = perform_xor(xor_byte, [ciphertext_arr[32+i]])[0]
    print(decryption_ctr_bitflip(ciphertext_arr))



if __name__ == "__main__":
    solve()
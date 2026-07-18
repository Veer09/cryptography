from utils.mac import verify_secret_prefix_mac
from utils.oracles import global_key
from utils.hash import SHA1
import struct
from utils.mac import secret_prefix_mac

message = b"comment1=cooking%20MCs;userdata=foo;comment2=%20like%20a%20pound%20of%20bacon"

def padding(len_message: int, len_key: int) -> bytes:
    len_data = len_key + len_message
    padding = b"\x80"
    while (len_data + len(padding) + 8) % 64 != 0:
        padding += b"\x00"
    length_in_bits = len_data * 8
    length = length_in_bits.to_bytes(8, 'big')
    padding += length
    return padding

def solve():
    tag = secret_prefix_mac(message)
    tag_bytes = bytes.fromhex(tag)
    tag_state = list(struct.unpack(">5I", tag_bytes))
    for i in range(8, 48):
        padd = padding(len(message), i)
        sha1 = SHA1(tag_state, start_len=len(message) + i + len(padd))
        forge_text_bytes = b";admin=true"
        new_message = message + padd + forge_text_bytes
        forge_tag = sha1.compute_hash(forge_text_bytes)
        if verify_secret_prefix_mac(new_message, forge_tag):
            print("Length of key:", i)
            print("Cracked!!")
            
    

if __name__ == "__main__":
    solve()
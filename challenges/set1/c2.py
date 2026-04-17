from utils import hex_to_bytes, perform_xor

hex1 = "1c0111001f010100061a024b53535009181c"
hex2 = "686974207468652062756c6c277320657965"

def solve():
    print(perform_xor(hex_to_bytes(hex1), hex_to_bytes(hex2)).hex())

if __name__ == "__main__":
    solve()

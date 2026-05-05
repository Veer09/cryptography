
from utils import remove_pkcs7_padding
valid_1 = b"ICE ICE BABY\x04\x04\x04\x04"
invalid_1 = b"ICE ICE BABY\x05\x05\x05\x05"
invalid_2 = b"ICE ICE BABY\x01\x02\x03\x04"

def solve():
    print(remove_pkcs7_padding(valid_1))
    # print(remove_pkcs7_padding(invalid_1))
    # print(remove_pkcs7_padding(invalid_2))

if __name__ == "__main__":
    solve()
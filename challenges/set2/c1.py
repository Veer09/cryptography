from utils import pkcs7_padding
plain_text = "YELLOW SUBMARINE"

def solve():
    print(pkcs7_padding(plain_text.encode('utf-8'), 20))


if __name__ == "__main__":
    solve()
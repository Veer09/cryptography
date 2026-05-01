from utils import pkcs7_padding
from utils import decrypt_profile
from utils import encrypt_profile

def solve():
    role = "admin"
    #padded role: admin{padding} -> 16bytes
    padded_role = pkcs7_padding(role.encode(), 16)
    dummy_email = "A" * 10 + padded_role.decode('utf-8')
    #encoded profile: email=AAAAAAAAAAadmin{padding}
    #first block: email=AAAAAAAAAA
    #second block: admin{padding} -> which we will use to replace
    cipher = encrypt_profile(dummy_email)
    role_block = cipher[16:32]
    #No. of A's such that all email=A's&uid=10&role= treated as multiples of block
    #So, last block only encrypted user{padding} which we will eventually replace with encrypted admin{padding}
    email = "A" * 13
    cipher_user = encrypt_profile(email)
    trimmed_cipher = cipher_user[:-16]
    cipher_admin = trimmed_cipher + role_block
    print(decrypt_profile(cipher_admin)) 
        

if __name__ == "__main__":
    solve()
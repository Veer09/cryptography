# pyrefly: ignore [missing-import]
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# pyrefly: ignore [missing-import]
from cryptography.hazmat.backends import default_backend
from utils.xor import perform_xor




def pkcs7_padding(plaintext: bytes, block_size: int) -> bytes:
    padds = block_size - (len(plaintext) % block_size)
    padding = bytes([padds]) * padds
    return plaintext + padding


def remove_pkcs7_padding(plaintext: bytes) -> bytes:
    padds = plaintext[-1]
    if padds == 0 or padds > 16:
        raise ValueError("Invalid Padding Length!!")
    if plaintext[-padds:] != bytes([padds]) * padds:
        raise ValueError("Inavlid PKCS#7 Padding!!!")
    return plaintext[:-padds]


def decrypt_aes_ecb(ciphertext: bytes, key: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()


def encrypt_aes_ecb(plaintext: bytes, key: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(plaintext) + encryptor.finalize()


def decrypt_aes_cbc(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    plaintext = bytearray()
    previous = iv
    for i in range(0, len(ciphertext), 16):
        block = ciphertext[i : i + 16]
        pt = decrypt_aes_ecb(block, key)
        plaintext.extend(perform_xor(pt, previous))
        previous = block
    return bytes(plaintext)


def encrypt_aes_cbc(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    padded_text = pkcs7_padding(plaintext, 16)
    ciphertext = bytearray()
    previous = iv
    for i in range(0, len(padded_text), 16):
        block = padded_text[i : i + 16]
        ct = encrypt_aes_ecb(perform_xor(block, previous), key)
        previous = ct
        ciphertext.extend(ct)
    return bytes(ciphertext)


def detect_ecb(ciphertext: bytes) -> bool:
    blocks = {}
    for i in range(0, len(ciphertext), 16):
        key = ciphertext[i : i + 16]
        blocks[key] = blocks.get(key, 0) + 1
    for key in blocks:
        if blocks[key] > 1:
            return True
    return False


def generate_keystream(nonce: bytes, counter: bytes, key: bytes) -> bytes:
    iv = nonce + counter
    return encrypt_aes_ecb(iv, key)


def aes_ctr(text: bytes, key: bytes) -> bytes:
    nonce = 0
    blocks = -(len(text) // -16)
    cipher = b""
    for i in range(blocks):
        ks = generate_keystream(
            nonce.to_bytes(8, byteorder="little"),
            i.to_bytes(8, byteorder="little"),
            key,
        )
        block_text = text[i * 16 : (i + 1) * 16]
        cipher += perform_xor(ks[: len(block_text)], block_text)
    return cipher

class MT19937:
    def __init__(self, seed):
        self.n= 624
        self.m = 397
        self.f = 1812433253
        self.a = 0x9908B0DF
        self.lower_mask = (1 << 31) - 1
        self.upper_mask = 1 << 31
        self.index = self.n
        self.mask32 = 0xFFFFFFFF
        self.mt_state = [0] * self.n
        self.initialize_state(seed)
        
    def initialize_state(self, seed: int):
        #Initialization
        self.mt_state[0] = seed & self.mask32
        for i in range(1, 624):
            top_two = self.mt_state[i-1] >> 30
            # Adding multiplication avalanche in state
            self.mt_state[i] = (self.f * (self.mt_state[i-1] ^ top_two) + i) & self.mask32

    def twist_state(self):
        for i in range(self.n):
            x = (self.mt_state[i] & self.upper_mask) + (self.mt_state[(i+1) % self.n] & self.lower_mask)
            xA = x >> 1
            if x % 2 != 0:
                xA ^= self.a
            self.mt_state[i] = (self.mt_state[ (i + self.m) % self.n] ^ xA) & self.mask32
        self.index = 0

    def temper(self):
        if self.index == self.n:
            self.twist_state()
        y = self.mt_state[self.index]
        y ^= (y >> 11)
        y ^= (y << 7) & 0x9D2C5680
        y ^= (y << 15) & 0xEFC60000
        y ^= (y >> 18)
        self.index += 1
        return y & self.mask32

    def generate_number(self):
        return self.temper()


    

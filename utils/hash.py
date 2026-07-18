import struct


class SHA1:
    def __init__(self):
        self.K = [0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xCA62C1D6]
        self.block_size = 512
        self.length_field = 64

    def _f(self, i: int, b: int, c: int, d: int) -> int:
        if i < 20:
            return (b & c) | ((~b) & d)
        elif i < 40:
            return b ^ c ^ d
        elif i < 60:
            return (b & c) | (b & d) | (c & d)
        else:
            return b ^ c ^ d
    
    def compute_hash(self, data: bytes) -> str:
        self.digest = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]
        padded_data = self._padding(data)
        for i in range(0, len(padded_data), (self.block_size // 8)):
            self._compression_function(padded_data[i:i+(self.block_size // 8)])
        final_hash = f"{self.digest[0]:08x}{self.digest[1]:08x}{self.digest[2]:08x}{self.digest[3]:08x}{self.digest[4]:08x}"
        return final_hash
        
    def _padding(self, data: bytes) -> bytes:
        padding = b"\x80"
        while (len(data) + len(padding) + (self.length_field // 8)) % (self.block_size // 8) != 0:
            padding += b"\x00"
        length_in_bits = len(data) * 8
        length = length_in_bits.to_bytes((self.length_field // 8), 'big')
        padding += length
        return data + padding

    def _compression_function(self, data: bytes) -> bytes:
        block = list(struct.unpack(">16I", data))
        expanded_block = self._expand_words(block)
        a, b, c, d, e = self.digest
        for i in range(80):
            t = self._circular_left_32(a, 5) + self._f(i, b, c, d) + e + expanded_block[i] + self.K[i//20]
            t &= 0xFFFFFFFF
            e = d
            d = c
            c = self._circular_left_32(b, 30)
            b = a
            a = t
        self.digest[0] = (self.digest[0] + a) & 0xFFFFFFFF
        self.digest[1] = (self.digest[1] + b) & 0xFFFFFFFF
        self.digest[2] = (self.digest[2] + c) & 0xFFFFFFFF
        self.digest[3] = (self.digest[3] + d) & 0xFFFFFFFF
        self.digest[4] = (self.digest[4] + e) & 0xFFFFFFFF
            

    def _expand_words(self, block: list[int]) -> list[int]:
        expanded_block = block
        for i in range(16, 80):
            expanded_block.append(self._circular_left_32(expanded_block[i - 3] ^ expanded_block[i - 8] ^ expanded_block[i - 14] ^ expanded_block[i - 16], 1))    
        return expanded_block
    
    def _circular_left_32(self, n: int, amount: int) -> int:
        return ((n << amount) | (n >> (32 - amount))) & 0xFFFFFFFF
    
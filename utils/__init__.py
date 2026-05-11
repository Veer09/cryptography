from utils.encoding import hex_to_bytes, bytes_to_base64
from utils.xor import (
    perform_xor,
    single_byte_xor,
    repeated_key_xor,
    score_text,
    calculate_hamming_distance,
    find_key,
)
from utils.crypto import (
    decrypt_aes_ecb,
    encrypt_aes_ecb,
    decrypt_aes_cbc,
    encrypt_aes_cbc,
    pkcs7_padding,
    remove_pkcs7_padding,
    detect_ecb,
)
from utils.oracles import (
    encryption_oracle,
    new_oracle,
    kv_parsing,
    profile_for,
    encrypt_profile,
    decrypt_profile,
    new_oracle2,
    encryption_cbc_bitflip,
    decryption_cbc_bitflip,
    encryption_padding_oracle,
    padding_oracle,
)

__all__ = [
    # encoding
    "hex_to_bytes",
    "bytes_to_base64",
    # xor
    "perform_xor",
    "single_byte_xor",
    "repeated_key_xor",
    "score_text",
    "calculate_hamming_distance",
    "find_key",
    # crypto
    "decrypt_aes_ecb",
    "encrypt_aes_ecb",
    "decrypt_aes_cbc",
    "encrypt_aes_cbc",
    "pkcs7_padding",
    "remove_pkcs7_padding",
    "detect_ecb",
    # oracles
    "encryption_oracle",
    "new_oracle",
    "kv_parsing",
    "profile_for",
    "encrypt_profile",
    "decrypt_profile",
    "new_oracle2",
    "encryption_cbc_bitflip",
    "decryption_cbc_bitflip",
    "encryption_padding_oracle",
    "padding_oracle",
]

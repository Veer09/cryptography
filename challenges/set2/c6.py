from utils import new_oracle2

def solve():
    input_a = bytes([65]) 
    input_b = bytes([66])

    cipher_a = new_oracle2(input_a)
    cipher_b = new_oracle2(input_b)

    input_block_start = 0
    for i in range(0, len(cipher_a), 16):
        chunk_a = cipher_a[i:i+16]
        chunk_b = cipher_b[i:i+16]
        if chunk_a != chunk_b: 
            input_block_start = i
            break

    previous_cipher_chunk = cipher_a[input_block_start:input_block_start+16]
    number_as = 0
    for i in range(2, 18):
        input_as = bytes([65]) * i
        cipher_as = new_oracle2(input_as)
        cipher_as_chunk = cipher_as[input_block_start:input_block_start+16]
        if cipher_as_chunk == previous_cipher_chunk:
            input_bs = bytes([66]) * i
            input_bs_previous = bytes([66]) * (i-1)
            cipher_bs = new_oracle2(input_bs)
            cipher_bs_previous = new_oracle2(input_bs_previous)
            if cipher_bs[input_block_start:input_block_start+16] == cipher_bs_previous[input_block_start:input_block_start+16]:
                number_as = i - 1
                break
        previous_cipher_chunk = cipher_as_chunk

    random_prefix_length = input_block_start + (16 - number_as)

    iteration = 1 
    byte_no = 0
    fix_as = bytes([65]) * number_as
    test_bytes = bytes([65]) * (15)
    secret_msg = bytearray(test_bytes)
    while True:
        cipher = new_oracle2(fix_as + test_bytes[:(16 - (byte_no % 16))-1])
        cipher_map = {}
        for i in range(256):
            trial_byte = bytes([i])
            crafted_msg = fix_as + secret_msg[-(16-1):] + trial_byte
            ciphertext = new_oracle2(crafted_msg)
            cipher_map[ciphertext[random_prefix_length + number_as : random_prefix_length + number_as + 16]] = trial_byte
        target = cipher[random_prefix_length + number_as + ((iteration-1)*(16)): random_prefix_length + number_as + (iteration)*(16)]
        if target not in cipher_map:
            break
        if target in cipher_map:
            secret_msg.append(cipher_map[target][0]) 
            byte_no = byte_no + 1
        if byte_no % 16 == 0:
            iteration = iteration + 1
    print(bytes(secret_msg[(16-1):-1]).decode('utf-8'))

if __name__ == "__main__":
    solve()
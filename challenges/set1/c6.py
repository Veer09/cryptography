from utils import repeated_key_xor
from utils import find_key
import base64
from utils import calculate_hamming_distance

def solve():
    with open("challenges/set1/6.txt", "r") as f:
        data = base64.b64decode(f.read())
        ham_distances = []
        for key_size in range(2, 41):
            avg_distance = 0
            for i in range(3):
                first = data[i*key_size:(i+1)*key_size]
                second = data[(i+1)*key_size:(i+2)*key_size]
                avg_distance += (calculate_hamming_distance(first, second)/3)
            ham_distances.append((avg_distance/key_size, key_size)) 
        sorted_dist = sorted(ham_distances)
        best_score = float('-inf')
        best_key = b""
        for i in range(4):
            key_size = sorted_dist[i][1]
            total_score = 0
            final_key = bytearray()
            for key_index in range(0, key_size):
                block = bytearray()
                for j in range(key_index, len(data), key_size):
                    block.append(data[j])
                score, result, key = find_key(block)
                total_score += score 
                final_key.append(key)
            if total_score > best_score:
                best_score = total_score
                best_key = bytes(final_key)
        decrypted_result = repeated_key_xor(data, best_key)
        print(f"Key: {best_key.decode('utf-8', errors='replace')}")
        print(f"Decrypted Data: \n{decrypted_result.decode('utf-8', errors='replace')}")

if __name__ == "__main__":
    solve()
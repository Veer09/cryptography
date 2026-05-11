# Single-Byte XOR Attack

## What it breaks
This attack breaks ciphertexts that have been encrypted by XORing every single byte of the plaintext against the exact same single-byte key (a key that is only 1 byte, or 8 bits long).
$$C_i = P_i \oplus K$$
 
## The property being exploited
Because a single byte can only hold values from `0` to `255` (0x00 to 0xFF), the total keyspace is incredibly small: exactly **256 possible keys**. This allows us to use a **Brute Force Exhaustion** approach combined with **[Frequency Analysis](../../concepts/classical/frequency-analysis.md)** to instantly find the correct key.

## Steps
1. **Exhaust the Keyspace**: Because of the reversibility property of XOR ($P = C \oplus K$), we can simply loop through all 256 possible integers (`0` through `255`). For every iteration, we XOR the entire ciphertext against that integer.
2. **Score the Outputs**: We pass all 256 resulting plaintexts into a scoring function. If we decrypt with the wrong key, the output will look like random garbage with lots of non-printable characters. If we decrypt with the correct key, the output will look like standard English language.
3. **Frequency Analysis Rules**: To score the text programmatically, we assign positive points to common English characters (like `E`, `T`, `A`, `O`, `I`, `N`, and spaces) and penalize non-printable or rare characters.
4. **Select the Winner**: The plaintext that yields the highest statistical score is guaranteed to be our original text, and the integer that produced it is the secret key.

## The key insight
The non-obvious secret to writing this effectively in code is **penalizing bad characters!** While looking for `E` and `T` is important, strongly penalizing non-printable ASCII characters (like null bytes, tabs, or control characters) is what guarantees the correct English plaintext bubbles to the top of the scores perfectly every time.

## My implementation
*   **The Scoring Tool:** [`utils/xor.py (score_text)`](../../../utils/xor.py)
*   **The XOR Tool:** [`utils/xor.py (find_key)`](../../../utils/xor.py)
*   **The Full Challenge:** [`c3.py`](../../../challenges/set1/c3.py)

## Connected to
*   [XOR and Why It Is Used](../../concepts/classical/xor-and-why-it-is-used.md)
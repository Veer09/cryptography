# Breaking Repeated-Key XOR

## What it breaks
The **Repeated-Key XOR** (often related to the Vigenère cipher) is significantly more secure than a **[Single-Byte XOR](single-byte-xor.md)**. Instead of masking the entire plaintext with just one byte, it uses a key phrase of length $N$ and repeats it across the plaintext.

Because the key's length is completely unknown, it breaks classical **[Frequency Analysis](../../concepts/classical/frequency-analysis.md)**. The letter 'E' in the plaintext might be encrypted by the 1st byte of the key, but the next time 'E' appears, it might be encrypted by the 4th byte of the key! This destroys the statistical distribution, making the cipher look indistinguishable from randomness.

## The property being exploited
The Achilles heel of this cipher is the **repetition**. Even though the ciphertext is masked by a long key, **every $N$th character is encrypted using the exact same byte**. 

If we can mathematically deduce the key length $N$, we can shatter this complex cipher into $N$ separate, trivially easy Single-Byte XOR ciphers!

### The Magic Trick: Finding Key Length via [Hamming Distance](../../concepts/classical/hamming-distance.md)
To find the key length, we guess different sizes. For each guess $N$, we take the first block of ciphertext ($C_1$) and the second block ($C_2$).

Because of the identity properties of XOR, if we correctly guessed $N$, then $C_1$ and $C_2$ were encrypted using the exact same key block $K$. Look at what happens when we XOR them together:

$$C_1 \oplus C_2 = (P_1 \oplus K) \oplus (P_2 \oplus K) = P_1 \oplus P_2$$

> [!TIP]
> **The Secret:** The XOR completely cancels out the key! We are left comparing the two blocks of original, underlying plaintext. Because standard English text blocks are structured and share a low Hamming Distance, the correct key length guess will mathematically yield the **lowest normalized Hamming Distance**.

**What if we guess the wrong key length?**
If we guess wrong, the two blocks will be encrypted with completely misaligned, different key segments ($K_1$ and $K_2$).
$$C_1 \oplus C_2 = (P_1 \oplus K_1) \oplus (P_2 \oplus K_2) = P_1 \oplus P_2 \oplus K_1 \oplus K_2$$
Because $K_1$ and $K_2$ are different, the key no longer cancels out. We are left comparing two strings of random, chaotic bytes! Random ciphertext mathematically has a natively **higher** Hamming Distance compared to structured plaintext.

> [!WARNING]
> Because of natural statistical variance in English (or inadvertently guessing a multiple of the true key size, like 6 instead of 3), the absolute lowest distance isn't *always* the correct one. It's best practice to take the top 3 or 4 lowest distances and test them all!

## Attack Steps
1. **Guess `KEYSIZE`**: Loop through possible lengths.
2. **Calculate Hamming Distance**: For each `KEYSIZE`, calculate the normalized Hamming Distance between blocks. Select the top 3-4 lowest distances to attack.
3. **Break into Blocks**: Chop the entire ciphertext into blocks of size `KEYSIZE`.
4. **Transpose the Blocks**: This is the genius step that converts this complex cipher into multiple Single-Byte XORs. If our `KEYSIZE` is 3, the key is represented as $K_1, K_2, K_3$.
   - **Block 1:** $P_1(K_1), P_2(K_2), P_3(K_3)$
   - **Block 2:** $P_4(K_1), P_5(K_2), P_6(K_3)$
   - **Transposed Column 1:** $P_1, P_4, P_7$... all perfectly encrypted using **ONLY $K_1$**!
5. **Single-Byte Attack**: You now have `KEYSIZE` number of columns. As visualised above, every byte in a single column was encrypted using just one character of the key. You can now effortlessly break each column individually using standard **[Frequency Analysis](../../concepts/classical/frequency-analysis.md)** (**[Single-Byte XOR Attack](single-byte-xor.md)**).
6. **Reconstruct the Key**: Stitch the broken characters back together. You now hold the master passphrase!

## My implementation
*   **The Main Breaking Logic:** [`c6.py`](../../../challenges/set1/c6.py)

## Connected to
*   [XOR and Why It Is Used](../../concepts/classical/xor-and-why-it-is-used.md)
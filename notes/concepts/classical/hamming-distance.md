# Hamming Distance

## What it is
Hamming Distance (often referred to as Edit Distance at the bit-level) is a metric for comparing two binary strings of equal length. It represents the exact number of differing bits between them.

## The core intuition
Think of it as measuring *how many bit flips* it would take to mutate String A into String B. If the two strings are completely identical, the Hamming distance is 0. 

## The math (minimal)
Because of the properties of XOR, calculating the Hamming distance is incredibly simple. Recall that XOR outputs a `1` if two bits are different, and `0` if they are the same. 

Therefore, the Hamming Distance $H$ between strings $A$ and $B$ is the sum of the `1` bits (the population count, or `popcount`) of $A \oplus B$:

$H(A, B) = \sum (\text{bit\_count}(A \oplus B))$

## Why it matters for crypto
Hamming distance is the mathematical "magic trick" used to crack Repeating-Key XOR (Vigenère) ciphers. 

Because standard English text has a highly predictable distribution of bytes (mostly lowercase letters, spaces, and punctuation), the Hamming distance between two normal English blocks is statistically lower than the distance between purely random blocks.

When guessing a key size $N$, if you guess correctly, you are comparing bytes that were encrypted with the exact same key index. The XOR cancellation reveals the underlying low Hamming distance of English. If you guess incorrectly, you are comparing pseudo-random ciphertext to pseudo-random ciphertext, yielding a high, chaotic Hamming distance!

## Connected to
*   [XOR and Why It Is Used](xor-and-why-it-is-used.md)
*   [Repeating Key XOR Attack](../../attacks/xor-attacks/repeted-key-xor.md)
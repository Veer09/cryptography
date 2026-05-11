# Frequency Analysis

## What it is
Frequency Analysis is a classical cryptanalysis method used to break ciphers by analyzing the frequency of letters, pairs of letters, or byte strings in a ciphertext and comparing them to the known statistical distribution of a language.

## The core intuition
Because human languages have highly predictable patterns (like 'E' being everywhere and 'Z' being rare), any weak encryption that maps characters 1-to-1 will inherently leak those exact same patterns into the ciphertext.

## The math (minimal)
If $C$ is a ciphertext character encrypted via a 1-to-1 substitution function $f(P) = C$, the frequency probability remains preserved:
$P(C) \approx P(P \text{ in English})$

For example, if in English $P(\text{'E'}) \approx 12.7\%$, and in our ciphertext the character $\text{'X'}$ appears $\approx 12.7\%$ of the time, it is highly probable that $f(\text{'E'}) = \text{'X'}$. We then score variations of text (often called ETAOIN SHRDLU scoring) to mathematically find the most probable key.

## Why it matters for crypto
If an encryption algorithm preserves the frequency distribution of the plaintext (like Single-Byte XOR), the cipher is fundamentally broken. Modern cryptography dictates that ciphertexts must be indistinguishable from true randomness (where every bit has an exact 50-50 chance of being 1 or 0), completely destroying any frequency leakage.

## Connected to
*   [XOR and Why It Is Used](xor-and-why-it-is-used.md)
*   [Single-Byte XOR Attack](../../attacks/xor-attacks/single-byte-xor.md)
*   [Repeated-Key XOR Attack](../../attacks/xor-attacks/repeted-key-xor.md)
# Padding Oracle Attack

## What it breaks
The **[CBC Mode](../../concepts/modes-of-operation.md)** decryption formula is:

$$P_i = D(K,\ C_i) \oplus C_{i-1}$$

After decryption, most systems verify that the plaintext ends with valid **[PKCS#7 padding](../../concepts/pkcs7-padding.md)**. If padding is invalid, the system returns an error. If it is valid, processing continues normally.

This error signal — *valid padding* vs *invalid padding* — is the **oracle**. The attacker does not need the key, does not need to break AES, and does not even need to encrypt anything. They only need to repeatedly ask the question: *"Does this ciphertext, when decrypted, have valid padding?"* The answer leaks enough information to recover the entire plaintext, one byte at a time.


## What PKCS#7 padding looks like
PKCS#7 padding fills the last block to the full block size. The padding byte value equals the number of padding bytes added:

```
1 byte  of padding:  ... [ XX  XX  XX  XX  XX  XX  XX  XX  XX  XX  XX  XX  XX  XX  XX  01 ]
2 bytes of padding:  ... [ XX  XX  XX  XX  XX  XX  XX  XX  XX  XX  XX  XX  XX  XX  02  02 ]
3 bytes of padding:  ... [ XX  XX  XX  XX  XX  XX  XX  XX  XX  XX  XX  XX  XX  03  03  03 ]
```

The oracle accepts any of these patterns and rejects anything else.

## The property being exploited
From the [Bit-Flipping Attack](bit-flipping.md) we know that modifying $C_{i-1}$ produces a **predictable, controlled change** in $P_i$ through XOR:

$$P_i[j] = D(K,\ C_i)[j] \oplus C_{i-1}[j]$$

Here $D(K, C_i)[j]$ is a fixed, unknown intermediate value. Call it $X[j]$ to keep things clean:

$$P_i[j] = X[j] \oplus C_{i-1}[j]$$

If the attacker replaces $C_{i-1}[j]$ with a trial value $t$, the decrypted byte becomes:

$$P_i'[j] = X[j] \oplus t$$

The attacker does not know $X[j]$, but they can try all 256 values of $t$. When the oracle says "valid padding", that gives a constraint on what $P_i'[j]$ must be — and from that, $X[j]$ can be calculated. Since $X[j]$ is fixed:

$$X[j] = P_i'[j] \oplus t$$
$$P_i[j] = X[j] \oplus C_{i-1}[j] = P_i'[j] \oplus t \oplus C_{i-1}[j]$$

The original plaintext byte is now known.

## Walking through the attack: recovering the last byte

### Setup
Take any two consecutive ciphertext blocks $(C_1, C_2)$. The goal is to recover $P_2$ (the plaintext of the second block). The original $C_1$ is kept on the side; a **modified copy** $C_1'$ is built to probe the oracle.

### Step 1 — Probe for valid `\x01` padding
Try all 256 values for $C_1'[15]$ (the last byte of $C_1'$). Send $(C_1', C_2)$ to the oracle for each trial. When the oracle returns **valid**, the decrypted last byte $P_2'[15]$ must equal `\x01` — because a single-byte pad of `\x01` is the only one-byte valid PKCS#7 ending.

Let the winning trial value be $t^*$. Then:

$$P_2'[15] = \texttt{0x01}$$
$$X[15] = \texttt{0x01} \oplus t^*$$
$$P_2[15] = X[15] \oplus C_1[15] = \texttt{0x01} \oplus t^* \oplus C_1[15]$$

The last byte of the original plaintext is recovered.

### Step 2 — False positive guard
There is one edge case: the last byte of $P_2$ might already be `\x02`, and the second-last byte might also be `\x02`. In that case, the oracle would say "valid" for the trial value that produces `\x02 \x02` at the end — a false positive that looks like 2-byte padding, not 1-byte padding.

To catch this, when the oracle first says "valid" for $C_1'[15] = t^*$, flip one more bit — XOR $C_1'[14]$ (the second-last byte) by `\x01` and re-query the oracle. If it now says "invalid", the `\x02\x02` false positive is confirmed. Continue searching. If it still says "valid", the `\x01` reading is genuine.

This is exactly what `c1.py` does:
```python
if is_first:
    cipher_arr[15 - j - 1] ^= 1       # disturb the byte before
    if not padding_oracle(iv, bytes(cipher_arr)):
        continue                        # false positive — keep searching
```

## Recovering the second-last byte (generalising the pattern)

Once $P_2[15]$ is known, the next goal is $P_2[14]$. For this, the oracle needs to see `\x02 \x02` at the end of $P_2'$ — two-byte valid padding.

### Step 1 — Set up the last byte as `\x02`
Using the bit-flipping formula, compute a new $C_1'[15]$ that forces $P_2'[15] = \texttt{0x02}$:

$$C_1'[15] = X[15] \oplus \texttt{0x02}$$

We already know $X[15]$ from the previous step, so this is a direct calculation — no brute-force needed.

### Step 2 — Brute-force the second-last byte
Now try all 256 values for $C_1'[14]$ while keeping $C_1'[15]$ fixed at the value that gives `\x02`. When the oracle says "valid", the last two bytes of $P_2'$ are `\x02 \x02`:

$$P_2'[14] = \texttt{0x02}$$
$$X[14] = \texttt{0x02} \oplus t^*$$
$$P_2[14] = X[14] \oplus C_1[14]$$

Second-last byte recovered. In `c1.py`, after each byte is found, all already-solved positions are flipped to the next padding target value in one pass:

```python
for m in range(j + 1):
    selected_cipher[15 - m] ^= last_padding ^ (last_padding + 1)
last_padding += 1
```

This prepares all previously solved bytes to produce the next padding value (`\x02` → `\x03` → `\x04` ...) ready for the next round of brute-force.

## The general pattern

For the $k$-th byte from the end (0-indexed), the target padding value is $k+1$. All bytes after position $15-k$ are already known, so they can be set precisely via the bit-flipping formula to produce the required padding tail. Only one byte — $C_1'[15-k]$ — is brute-forced.

**Per-byte cost:** at most 256 oracle queries.
**Per-block cost:** $16 \times 256 = 4096$ oracle queries at most.
**Full message of $n$ blocks:** at most $n \times 4096$ queries.

The formula that converts a winning trial $t^*$ for byte $k$ from the end into an original plaintext byte is always:

$$\boxed{P_2[15-k] = (k+1) \oplus t^* \oplus C_1[15-k]}$$

## Recovering multiple blocks
The attack is not limited to two blocks. The full ciphertext is treated as a sequence of pairs: $(C_0, C_1)$, $(C_1, C_2)$, $(C_2, C_3)$, $\ldots$. The attack is run independently on each pair to recover the plaintext of the second block in each pair.

For the very first block, the IV plays the role of $C_0$ — which is exactly how `c1.py` handles it:

```python
cipher_iv = iv + cipher_only           # prepend IV so it acts as C0
for k in range(iterations - 1):
    selected_cipher = cipher_iv[k*16 : (k+2)*16]   # take two blocks at a time
```

## Root causes
The attacker never provides plaintext input to an encryption function. They work entirely with an existing ciphertext and a decryption endpoint that leaks only one bit per query: valid or invalid padding. The attack succeeds because:

1. **CBC's XOR chaining is malleable** — modifying $C_{i-1}$ gives precise control over $P_i$.
2. **Padding validation is a side channel** — the error message leaks information about the internal decrypted value.

These two properties together are sufficient to fully decrypt any CBC ciphertext without the key.

> [!WARNING]
> Any system that decrypts first and checks padding second — and reveals the result of that check, even just as "error 500 vs 200" — is vulnerable. The fix is **Encrypt-then-MAC**: authenticate the ciphertext before decrypting it, so tampered ciphertexts are rejected before padding is ever checked.

## My Implementation
- [`c1.py`](../../../challenges/set3/c1.py)

## Connected to
- [Modes of Operation (CBC)](../../concepts/modes-of-operation.md)
- [Bit-Flipping Attack](bit-flipping.md)
- [XOR and Why It Is Used](../../concepts/xor-and-why-it-is-used.md)
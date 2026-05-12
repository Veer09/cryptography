# Modes of Operation (ECB, CBC, CTR)

## What it is
**[AES](aes.md)** is a **block cipher** — it operates on exactly one fixed-size chunk of data at a time (16 bytes). Real-world data is almost always larger than 16 bytes, so we need a strategy for *how* to apply AES repeatedly across the full message.

A **Mode of Operation (MOO)** defines exactly that strategy: how to split the plaintext into blocks, whether to mix in any extra state between blocks, and how to combine the results into a final ciphertext. The choice of mode is a design decision with serious security consequences.

There are three modes covered here:
1. **Electronic Codebook Mode (ECB)** — the simplest, most dangerous mode.
2. **Cipher Block Chaining Mode (CBC)** — the classic fix that adds inter-block dependency.
3. **Counter Mode (CTR)** — turns the block cipher into a highly parallelisable stream cipher.

---

## 1. Electronic Codebook Mode (ECB)

### How it works
ECB is the most straightforward application of a block cipher. The plaintext is divided into **blocks** $P_1, P_2, \ldots, P_n$ of 16 bytes each, and each block is encrypted **completely independently** using the same key $K$.

**Encryption:**
$$C_i = E(K,\ P_i)$$

**Decryption:**
$$P_i = D(K,\ C_i)$$

Each block is a completely isolated operation — no block knows anything about the blocks before or after it.

### The critical weakness: pattern leakage
Because there is no mixing between blocks, **identical plaintext blocks always produce identical ciphertext blocks**:

$$P_i = P_j \implies C_i = C_j$$

This is not a bug in AES itself — AES is secure at the block level. The problem is in how ECB *applies* AES across a message. The structure of the original plaintext bleeds straight through into the ciphertext.

**Example:** A 48-byte message made of three identical 16-byte blocks:

```
Plaintext:  [ AAAAAAAAAAAAAAAA ]  [ AAAAAAAAAAAAAAAA ]  [ AAAAAAAAAAAAAAAA ]
Ciphertext: [    0xFA3C...D9  ]  [    0xFA3C...D9  ]  [    0xFA3C...D9  ]
                 same                 same                 same
```

An attacker who sees only the ciphertext immediately knows all three blocks were identical — without ever knowing the key. For structured data (JSON payloads, HTTP headers, images), this leaks enormous amounts of information.

> [!WARNING]
> **ECB determinism:** The mapping from plaintext block to ciphertext block under a fixed key is a permanent, stateless lookup table. Every time you encrypt the same 16-byte block with the same key, you get back the exact same 16 bytes of ciphertext — regardless of when, where, or how many times you do it.

### Detecting ECB in the wild
Because identical plaintext blocks produce identical ciphertext blocks, ECB is **detectable without the key**. Feed the oracle 32 or more identical bytes. If any two 16-byte blocks in the ciphertext output are identical, the mode is ECB.

### Known risks
Since the mode's core property is deterministic, stateless block encryption, several attacks become possible:

- **Byte-at-a-Time Decryption:** An attacker with oracle access can recover a secret suffix byte by byte by exploiting the deterministic block mapping. See [Byte-at-a-Time ECB Decryption](../../attacks/block-cipher-attacks/byte-at-a-time.md).
- **Block replay / substitution:** Because blocks are completely independent, an attacker can copy, reorder, or replay ciphertext blocks freely. A block $C_j$ that encrypts `"admin=true"` can be spliced into any position in any ciphertext — the other blocks decrypt correctly, unaware of the swap.
- **ECB Oracle Detection:** Covered in the cryptopals implementation at [`c3.py`](../../../challenges/set2/c3.py).

---

## 2. Cipher Block Chaining Mode (CBC)

### How it works
CBC fixes ECB's pattern leakage by **chaining** each block to the one before it. Before a plaintext block is encrypted, it is first **XOR'd** with the previous ciphertext block. This means even if two plaintext blocks are identical, they produce different ciphertext because they are XOR'd with different preceding ciphertext.

The first block has no predecessor, so an extra value called the **Initialisation Vector (IV)** stands in as $C_0$.

**Encryption:**
$$C_0 = IV$$
$$C_i = E(K,\ P_i \oplus C_{i-1})$$

**Decryption:**
$$P_i = D(K,\ C_i) \oplus C_{i-1}$$

The XOR with the previous ciphertext block means the encryption of $P_i$ now depends on every block before it. Two identical plaintext blocks at different positions will produce different ciphertext blocks because their preceding ciphertext blocks differ:

$$P_i = P_j\ \text{and}\ C_{i-1} \neq C_{j-1} \implies C_i \neq C_j$$

The plaintext pattern is completely hidden. The ECB determinism problem is gone.

### The role of the IV
The IV is a **16-byte value** used to start the chain. It XORs with $P_1$ before the first AES call, and its effect propagates forward to every subsequent block through the chain. This means:

- The entire ciphertext changes if the IV changes, even if the key and plaintext are identical.
- The IV **must be random and unique** for every single message encrypted under the same key. If the same $(K, IV)$ pair is reused for two messages, the first ciphertext block of both messages was encrypted from the same starting point: $E(K,\ P_1^{(A)} \oplus IV)$ and $E(K,\ P_1^{(B)} \oplus IV)$. XOR-ing those two first blocks cancels the key and reveals the XOR of the plaintexts — leaking structure even without key recovery.
- The IV is **not a secret**. It is sent alongside the ciphertext in plaintext because the receiver needs it to decrypt $P_1$. Secrecy of the IV is not required for confidentiality — only randomness and non-reuse are.
- Tampering with the IV is contained: it corrupts only $P_1$ during decryption (because the decryption of $P_1$ is the only place IV appears in the formula). $P_2, P_3, \ldots$ are unaffected. See the bit-flipping section below for how this property is exploited.

### What still goes wrong
CBC fixes ECB's weaknesses but introduces its own. The XOR-based chaining creates a **malleability** property: modifying a ciphertext block produces a predictable, controlled change in the *next* plaintext block after decryption.

From the decryption formula:

$$P_i = D(K,\ C_i) \oplus C_{i-1}$$

$P_i$ depends on $C_{i-1}$ through a plain XOR. If an attacker flips bit $b$ in $C_{i-1}$, bit $b$ in $P_i$ flips deterministically — no key required. The attacker sacrifices $P_{i-1}$ (which decrypts to garbage because $C_{i-1}$ was corrupted) to inject a chosen value into $P_i$.

> [!WARNING]
> **This only affects integrity, not confidentiality.** CBC still hides the plaintext contents. But it provides no guarantee that the plaintext you receive is the plaintext that was sent. Authenticated encryption (e.g. AES-GCM) solves this.

### Known risks
- **Bit-Flipping Attack:** An attacker who knows or can guess the structure of a plaintext block can flip bits in the preceding ciphertext block to produce a chosen change in the target block — for example, escalating `role=user` to `role=admin`. See [Bit-Flipping Attack](../../attacks/block-cipher-attacks/bit-flipping.md).
- **Padding Oracle Attack:** When a decryption endpoint leaks whether the PKCS#7 padding on the last block is valid or not, an attacker can exploit CBC's XOR chaining to decrypt any ciphertext byte by byte with no key. See [Padding Oracle Attack](../../attacks/block-cipher-attacks/padding-oracle.md).

---

## 3. Counter Mode (CTR)

### How it works
CTR mode is fundamentally different from ECB and CBC. Instead of encrypting the plaintext directly through the AES algorithm, CTR mode turns the block cipher into a **stream cipher**. It does this by encrypting a sequence of unique numbers (counters) to generate a pseudorandom sequence of bytes called a **keystream**. 

This keystream is then simply **XOR'd** with the plaintext to produce the ciphertext.

Each block requires a unique input to AES. This is created by combining:
1. **Nonce**: A unique value chosen once per message (similar to an IV). It ensures different messages get completely different keystreams.
2. **Counter**: A sequential number that increments for every block within the message.

**Keystream Generation:**
$$KS_i = E(K,\ \text{Nonce} \mathbin{\|} \text{Counter}_i)$$

**Encryption:**
$$C_i = P_i \oplus KS_i$$

**Decryption:**
$$P_i = C_i \oplus KS_i$$

Because encryption and decryption are just XORing with the same keystream, **the AES decryption function $D(K, \cdot)$ is never used** in CTR mode. Both operations use the AES encryption function $E(K, \cdot)$ to generate the keystream.

### What CTR fixes over CBC
CTR mode brings two massive architectural advantages over CBC:

1. **Parallelism**: Since the keystream blocks only depend on the key, nonce, and the block index (counter), they can all be computed independently at the same time. You can encrypt or decrypt the 100th block without needing to process blocks 1 through 99.
2. **No Padding Required**: Because it operates like a stream cipher, if the final plaintext block is only 5 bytes long, you simply take the first 5 bytes of the final keystream block and XOR them. The rest of the keystream block is discarded. Without padding, **padding oracle attacks are impossible**.

### The critical weakness: Nonce reuse
The entire security of CTR mode rests on one absolute rule: **you must never reuse the same (Key, Nonce) pair**.

If the same nonce is used for two different messages under the same key, the keystream generated will be perfectly identical for both messages. This leads to a catastrophic failure known as a **keystream reuse attack**.

If two plaintexts $P^{(A)}$ and $P^{(B)}$ are encrypted with the same keystream $KS$:
$$C^{(A)} = P^{(A)} \oplus KS$$
$$C^{(B)} = P^{(B)} \oplus KS$$

An attacker can XOR the two ciphertexts together, which cancels out the unknown keystream entirely and leaves the XOR of the two plaintexts:
$$C^{(A)} \oplus C^{(B)} = P^{(A)} \oplus P^{(B)}$$

From $P^{(A)} \oplus P^{(B)}$, an attacker can use frequency analysis and crib-dragging to recover both plaintexts, completely breaking the encryption without ever finding the key.

### What still goes wrong: severe malleability
Like CBC mode, CTR mode provides no integrity. But CTR is even **more vulnerable to bit-flipping** than CBC.

In CBC, flipping a bit in the ciphertext allows you to control the next block's plaintext, but it completely destroys the current block. 
In CTR mode, the malleability is perfectly surgical:
$$P_i'[j] = P_i[j] \oplus (C_i[j] \oplus C_i'[j])$$

If an attacker flips the $j$-th bit of $C_i$, the exact same bit flips in $P_i$ — and **no other bits or blocks are affected**. There is zero collateral damage. An attacker who knows the plaintext can modify it to anything they want with perfect precision.

> [!WARNING]
> Because CTR is completely malleable, it must **never** be used without a Message Authentication Code (MAC) to guarantee integrity. Modern systems combine CTR mode with a Carter-Wegman MAC to create **AES-GCM** (Galois/Counter Mode) — the standard for authenticated encryption.

### Known risks
- **Nonce Reuse Attack:** XORing two ciphertexts encrypted with the same nonce reveals the XOR of their plaintexts. See the dedicated attack writeup *(coming soon)*.
- **Bit-Flipping Attack:** CTR is completely malleable with no block sacrifice, allowing surgical tampering of the plaintext.

---

## Summary

| Property | ECB | CBC | CTR |
|---|---|---|---|
| Inter-block dependency | None | $C_i$ depends on all previous blocks via chain | None |
| Same plaintext → same ciphertext? | Always (dangerous) | No — IV/Nonce break this | No — Nonce/Counter break this |
| Parallel encryption | Yes | No — each block needs the previous ciphertext | Yes |
| Parallel decryption | Yes | Yes — only needs $C_i$ and $C_{i-1}$ | Yes |
| Padding required | Yes | Yes | No |
| Main weakness | Pattern leakage, replay | Bit-flipping, padding oracle, IV reuse | Nonce reuse, surgical bit-flipping |

## Connected to
- [AES](aes.md)
- [XOR and Why It Is Used](../classical/xor-and-why-it-is-used.md)
- [Byte-at-a-Time ECB Decryption](../../attacks/block-cipher-attacks/byte-at-a-time.md)
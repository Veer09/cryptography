# Bit-Flipping Attack

## What it breaks
The **[CBC Mode](../../concepts/modes-of-operation.md)** encryption adds inter-block dependency to fix ECB's pattern leakage. However, CBC introduces a new problem: it is **malleable**. An attacker who can modify the ciphertext can produce a **predictable, controlled change** in the decrypted plaintext — without ever knowing the key.

This attack falls under **chosen-ciphertext manipulation** — the attacker does not try to decrypt anything. Instead, they tamper with the ciphertext bytes and let the decryption system do the work for them.

## The property being exploited
Recall the CBC decryption formula from [Modes of Operation](../../concepts/modes-of-operation.md):

$$P_i = D(K,\ C_i) \oplus C_{i-1}$$

The decrypted plaintext of block $i$ is produced by XOR-ing the raw AES decryption of $C_i$ with the **previous ciphertext block** $C_{i-1}$.

Now, $D(K, C_i)$ is completely fixed — it depends only on the key and the ciphertext block $C_i$, neither of which the attacker changes. That means:

$$P_i = \underbrace{D(K,\ C_i)}_{\text{fixed}} \oplus C_{i-1}$$

If the attacker flips a bit in $C_{i-1}$, that exact same bit flips in $P_i$ after decryption. The relationship is a direct XOR — perfectly predictable.

> [!TIP]
> **The core insight:** XOR is its own inverse. If $P_i = X \oplus C_{i-1}$, and you want a different $P_i' = X \oplus C_{i-1}'$, you just need $C_{i-1}' = C_{i-1} \oplus P_i \oplus P_i'$. You can compute this without knowing $X$ (the AES output) at all.

## The trade-off: one block is sacrificed
Flipping bits in $C_{i-1}$ controls $P_i$, but it also **destroys $P_{i-1}$**. From the decryption formula:

$$P_{i-1} = D(K,\ C_{i-1}) \oplus C_{i-2}$$

When $C_{i-1}$ is modified, the AES decryption $D(K, C_{i-1})$ produces a completely random, unpredictable output (AES is a pseudorandom permutation — any single bit change causes avalanche). So $P_{i-1}$ decrypts to garbage.

The attacker **sacrifices block $i-1$** (accepts that it becomes unreadable) to inject a chosen value into block $i$.

> [!WARNING]
> This attack only breaks **integrity**, not **confidentiality**. CBC still hides the plaintext contents correctly. But it provides zero guarantee that the plaintext you receive is the plaintext that was originally encrypted. Any system that relies on the ciphertext alone to protect data values (no message authentication) is vulnerable.

## Walking through the attack

### The setup
The oracle prepends and appends fixed strings to the attacker's input before encrypting:

```
"comment1=cooking%20MCs;userdata=" + attacker-input + ";comment2=%20like%20a%20pound%20of%20bacon"
```

The oracle also strips any `;` and `=` characters from the attacker's input to prevent direct injection. The goal is to get the string `;admin=true;` inside the decrypted plaintext.

### Step 1 — Craft the input
Since `;` and `=` are stripped, the attacker submits characters that are close but off by one bit:

- `:` instead of `;` (ASCII 0x3A vs 0x3B — differ by 1 bit)
- `<` instead of `=` (ASCII 0x3C vs 0x3D — differ by 1 bit)

Attacker sends: `:admin<true:`

The oracle encrypts:
```
Block 1 (16 bytes): "comment1=cooking"
Block 2 (16 bytes): "%20MCs;userdata="
Block 3 (16 bytes): ":admin<true:;com"   ← attacker-controlled block
Block 4 (16 bytes): "ment2=%20like%20"
Block 5 (16 bytes): "a%20pound%20of%2"
Block 6 (16 bytes): "0bacon" + padding
```

### Step 2 — Identify the target bits
The attacker wants `P_3` to become `;admin=true;com` instead of `:admin<true:;com`.

Three bytes in $P_3$ need to change:
- Position 0: `:` (0x3A) → `;` (0x3B) — flip bit 0
- Position 6: `<` (0x3C) → `=` (0x3D) — flip bit 0
- Position 11: `:` (0x3A) → `;` (0x3B) — flip bit 0

Each change is just XOR with `0x01` (flips the lowest bit).

### Step 3 — Modify the previous ciphertext block
To control $P_3$, the attacker modifies $C_2$ (the ciphertext of block 2). Specifically, at each target position $j$ within the block:

$$C_2'[j] = C_2[j] \oplus P_3[j] \oplus P_3'[j]$$

Since the required change at each position is just `0x01`:

$$C_2'[j] = C_2[j] \oplus \texttt{0x01}$$

In the implementation (`c8.py`), this is done at offsets 0, 6, and 11 within block 2 (bytes 16, 22, and 27 of the full ciphertext array):

```python
modification_bytes = [0, 6, 11]   # positions within block 2
xor_byte = bytes([1])              # flip 1 bit at each position
for i in modification_bytes:
    ciphertext_arr[16 + i] ^= 1
```

### Step 4 — Submit the tampered ciphertext
The attacker passes the modified ciphertext to the decryption oracle:

- $P_2'$ — decrypts to garbage (block 2 is sacrificed, but the comment text doesn't matter)
- $P_3'$ — decrypts to `;admin=true;com` ✓

The decryption system then finds `;admin=true;` in the plaintext and grants admin access — without the attacker ever knowing the key.

## Precise formula for the flip
If you know the current plaintext value $P_i[j]$ at byte position $j$ inside block $i$, and you want it to become $P_i'[j]$, modify $C_{i-1}[j]$ as:

$$C_{i-1}'[j] = C_{i-1}[j] \oplus P_i[j] \oplus P_i'[j]$$

This works because:

$$P_i'[j] = D(K,\ C_i)[j] \oplus C_{i-1}'[j]$$
$$= D(K,\ C_i)[j] \oplus C_{i-1}[j] \oplus P_i[j] \oplus P_i'[j]$$
$$= P_i[j] \oplus P_i[j] \oplus P_i'[j]$$
$$= P_i'[j] \checkmark$$

## What if the target is not block-aligned?

In the worked example above, the attacker's input `:admin<true:` happened to land exactly at the start of block 3. Real scenarios are rarely that clean.

### Target bytes inside a block (easy case)
The byte offset within a block does not matter at all. The formula $C_{i-1}'[j] = C_{i-1}[j] \oplus P_i[j] \oplus P_i'[j]$ works for any $j$ from 0 to 15. If the byte you want to change is at position 9 inside block 3, you modify byte 9 of $C_2$. Alignment within a block is never a problem.

### Target bytes spanning a block boundary (harder case)
If the bytes you want to change are split across two different blocks — say bytes 14–15 of block 3 and bytes 0–1 of block 4 — you need to modify **two different preceding ciphertext blocks** ($C_2$ and $C_3$). This sacrifices **two blocks** of plaintext instead of one.

More importantly, modifying $C_3$ also randomises $P_3$ via AES avalanche. If bytes 0–13 of block 3 were carrying data you needed intact (e.g. part of a previous field), they are now destroyed. The attacker has to decide whether the garbage in those blocks matters to the application.

> [!TIP]
> A common strategy to avoid cross-boundary problems is to **pad the attacker's input** so that the sensitive target bytes fall neatly at the start of a block. This is the same alignment trick used in [Byte-at-a-Time](../byte-at-a-time.md) to neutralise a random prefix.

---

## What if the target is the first block?

In standard CBC, modifying ciphertext block $C_{i-1}$ to flip bits in $P_i$ always destroys $P_{i-1}$. But when the target is $P_1$ (the very first plaintext block), the "previous block" is the **IV**, not a ciphertext block.

$$P_1 = D(K,\ C_1) \oplus IV$$

The IV is transmitted alongside the ciphertext (it is not encrypted — the receiver needs it in plaintext to decrypt). This means:

$$IV'[j] = IV[j] \oplus P_1[j] \oplus P_1'[j]$$

Submitting the modified $IV'$ produces the chosen $P_1'$ after decryption. Crucially, **no block is sacrificed** — $C_1, C_2, \ldots$ are untouched, so $P_2, P_3, \ldots$ all decrypt correctly. The attacker gets a precise single-block modification with zero collateral damage.

This makes IV-flipping a stronger variant of the attack when the first block is the target — for example, changing `role=user;padding` in $P_1$ to `role=admin;paddi`.

> [!WARNING]
> Systems that accept the IV from the user (e.g. stored as a cookie field, or sent as a request header) are especially exposed. If there is no integrity check on the IV, an attacker can flip any bit in $P_1$ for free.

---

## What if user input is not given at all?

The examples above assume the attacker can feed input to an encryption oracle to position their data into a known block. But bit-flipping does not strictly require an oracle. It only requires two things:

1. The attacker can **intercept and modify** the ciphertext in transit (man-in-the-middle position).
2. The attacker **knows or can guess** the plaintext at the specific byte positions they want to change.

### Known-plaintext scenario
Suppose the protocol always produces the same structure, and the attacker has learned the plaintext value at some position — either from a leaked message, from observing many responses, or because the protocol header is fixed and public (e.g. it always starts with `{"version":1,"user":"`).

If the attacker knows $P_i[j]$ and wants $P_i'[j]$, they can directly compute and apply $C_{i-1}'[j] = C_{i-1}[j] \oplus P_i[j] \oplus P_i'[j]$ without ever having fed any input to an oracle.

**Example:** A server encrypts a session token as:
```
Block 1: {"id":1234567890,  ← attacker's own user ID (known completely)
Block 2: "role":"user"}     ← target field is here, in block 2
```
The attacker knows Block 1 exactly — it contains their own user ID, which they provided. They also know the fixed format of Block 2 from the protocol specification, so they know `"user"` sits at bytes 8–11 of Block 2. To change `"user"` → `"root"` they modify $C_1$ at those positions:

$$C_1'[j] = C_1[j] \oplus P_2[j] \oplus P_2'[j]$$

After decryption: $P_1$ becomes garbage (sacrificed), but $P_2$ now reads `"role":"root"}` — privilege escalated without ever touching the key.

### Cookie-forging scenario
A user receives their own encrypted cookie and knows their own data. Because they know the plaintext, they can flip bits in the preceding ciphertext block to modify fields in the next block — even though they never had any control over the oracle input. This is why CBC-encrypted cookies without a MAC (message authentication code) are fundamentally insecure.

> [!NOTE]
> The common defence against all forms of bit-flipping — with or without oracle access — is **authenticated encryption**. A MAC (or an AEAD mode like AES-GCM) detects any modification to the ciphertext or IV before decryption, so tampered messages are rejected outright.

---

## My Implementation
- [`c8.py`](../../../challenges/set2/c8.py)

## Connected to
- [Modes of Operation (CBC)](../../concepts/modes-of-operation.md)
- [XOR and Why It Is Used](../../concepts/xor-and-why-it-is-used.md)

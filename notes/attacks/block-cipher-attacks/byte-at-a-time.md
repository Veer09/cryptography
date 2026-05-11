# Byte-at-a-Time ECB Decryption

## What it breaks
**[AES-ECB](../../concepts/ciphers/modes-of-operation.md)** has a critical, well-known weakness: **identical plaintext blocks always produce identical ciphertext blocks**. This attack exploits that property to recover a secret string byte by byte, even though the attacker never holds the key.

It falls under the category of a **Chosen-Plaintext Attack (CPA)** — the attacker has **full control** over the input to an encryption function (an **oracle**) and can observe the resulting ciphertext. The attacker cannot see the key or the secret string directly, but they can probe the oracle as many times as they want.

The encryption oracle behaves like this:

$$\text{AES-ECB}(\text{attacker-input} \mathbin{\|} \text{secret-string},\ \text{key})$$

Where $\|$ means **concatenation** — the attacker's bytes are placed *before* the secret string, and the whole thing is encrypted together under a fixed, unknown key.

## The property being exploited
The Achilles heel of ECB is that it encrypts each **16-byte block** in complete isolation. There is no chaining, no randomness, no memory of previous blocks. The same 16 bytes in → the same 16 bytes out, always.

The attacker exploits this by **sliding** their known input against the unknown secret string, one byte at a time, until the entire secret is revealed.

> [!TIP]
> **The Core Idea:** If the attacker can craft an input such that only **one unknown byte** falls inside a block they control, they can simply try all 256 possible values for that byte, compare the ciphertext results to the oracle's output, and find an exact match — revealing that one byte for free.

## Visualising the Attack (Simple Case)

Assume a **16-byte block size**. The oracle is:
$$\text{AES-ECB}(\text{your-input} \mathbin{\|} \text{secret},\ \text{key})$$

Let the secret string start with `S E C R E T ...` (shown as single letters for clarity).

**Step 1 — Discover the first byte of the secret:**

Send 15 `A`s as input. The first block now looks like:

```
Block 1: [ A A A A A A A A A A A A A A A S ]
          |<--- 15 known bytes --->|  |^ 1 unknown |
```

The oracle encrypts this block and returns a ciphertext. Call it `target_cipher`.

Now, build a **lookup table**: send every possible 16-byte message of the form `AAAAAAAAAAAAAAA?` where `?` is each of the 256 byte values (0x00 to 0xFF). Encrypt each one and record:

$$\text{cipher-map}[\text{AES-ECB}(\texttt{AAAAAAAAAAAAAAA?})] = \texttt{?}$$

Finally, look up `target_cipher` in `cipher_map`. The match gives you the first byte of the secret!

**Step 2 — Discover the second byte:**

Now you know the first byte. Call it `s1`. Send 14 `A`s as input. Block 1 is:

```
Block 1: [ A A A A A A A A A A A A A A s1 S2 ]
          |<--- 14 known --->| |known| |^ unknown|
```

Rebuild the lookup table using `AAAAAAAAAAAAAA s1 ?` and find the match. You now know `s2`.

**Step 3 — Repeat until the block is full:**

Continue reducing your `A` padding by one each time, using your already-discovered bytes to fill the left side. After 16 steps you will have recovered all 16 bytes of block 1.

> [!WARNING]
> After recovering a full block of the secret, the strategy shifts slightly. You now use your **known secret bytes** (instead of `A`s) to pad the lookup table for the next block. See the *Beyond One Block* section below.

## Beyond One Block
Once all 16 bytes of the first secret block are known, the attack continues into the second block using the same sliding-window logic. For the 17th byte:

Send 15 `A`s as input. The oracle now produces two blocks:

```
Block 1: [ A A A A A A A A A A A A A A A s1 ]   ← 15 A's + first known secret byte
Block 2: [ s2 s3 s4 ... s16 s17 ]                ← 15 known secret bytes + 1 unknown
```

The `s1` that was pushed into Block 1 acts as part of the "known left side". The lookup table is now built using the last 15 **known secret bytes** (`s2` through `s16`) + `?`:

$$\text{cipher-map}[\text{AES-ECB}(s_2\ s_3\ \ldots\ s_{16}\ \texttt{?})] = \texttt{?}$$

Match Block 2's ciphertext against the map to find `s17`. The pattern continues indefinitely — each iteration, the window of known bytes slides forward by one, recovering the entire secret string.

## Harder Variant: Unknown Random Prefix

The oracle can be made harder with a random prefix prepended by the server:

$$\text{AES-ECB}(\text{random-prefix} \mathbin{\|} \text{attacker-input} \mathbin{\|} \text{secret},\ \text{key})$$

Now the attacker doesn't know *where* their input lands inside the ciphertext. Before the byte-at-a-time attack can begin, two things must be found:
1. **Which block** does the attacker's input fall in?
2. **How many bytes** of the random prefix spill into that block?

### Step 1 — Find the Attacker's Input Block
Send two single-byte inputs that differ (e.g., one `A` and one `B`). Compare the resulting ciphertexts block by block. The random prefix is fixed, so all blocks that contain *only* prefix bytes will be **identical** in both outputs. The **first block that differs** between the two outputs is the block where the attacker's input begins.

```
Input 'A':  [ prefix_block_1 | prefix_block_2 | prefix + A + secret... ]
Input 'B':  [ prefix_block_1 | prefix_block_2 | prefix + B + secret... ]
                same ✓           same ✓             DIFFERENT ✗  ← found it
```

Call the byte offset of this block `input_block_start`.

### Step 2 — Find How Many Prefix Bytes Are in the Input Block
The **input block** has the structure:

```
[ (some prefix bytes) | attacker-input | (initial secret bytes) ]
```

Let `p` = the number of prefix bytes that spill into this block. Our goal is to find `p`.

Keep increasing the input length (sending `AA`, `AAA`, `AAAA`, ...) while watching the input block's ciphertext. As long as there are secret bytes in the block, the output changes each time. The moment **two consecutive input lengths produce the same ciphertext** in the input block, the attacker's bytes have completely pushed out all secret bytes — the block now contains only `(prefix tail + all A's)`.

> [!TIP]
> **False Positive Guard:** When the block first stabilises, the first byte of the secret might coincidentally be `A`, giving a false match. To verify, repeat the same test using `B`s instead of `A`s. If both `A` and `B` tests stabilise at the same length, it's a true boundary. If only one does, it's a false positive — try the next length.

When the block stabilises at input length $L$:

$$p = 16 - L$$
$$\text{total prefix length} = \text{input-block-start} + p$$

### Step 3 — Neutralise the Prefix
Now that `p` is known, always prepend exactly `p` filler bytes to your input. This pads the prefix tail to a full block, effectively making the prefix completely disappear into whole, fixed blocks. From this point, the attack is identical to the simple case, just offset by `(input_block_start + p)` bytes in the ciphertext.

## Attack Steps

### Simple Case (no random prefix)
1. **Recover byte by byte**: For each target byte position, send a short-by-one-byte input so one unknown byte lands in your target block. Build a 256-entry lookup table. Match the oracle's output to find the byte.
2. **Advance the window**: Append each found byte to your known secret and reduce the padding by one, continuing to the next byte.
3. **Cross block boundaries**: Once a block is fully recovered, use the last 15 known secret bytes as the left-side of your lookup table to probe the next block.
4. **Stop condition**: The loop ends when the oracle's target block can no longer be found in the lookup table.

   **Why does this happen?** AES-ECB requires the input to always be a multiple of 16 bytes, so the oracle internally applies PKCS#7 Padding to the plaintext before encrypting. When all real secret bytes have been recovered, padding bytes start appearing inside the target block, eventually causing a lookup miss.

   Trace through a 16-byte secret (`s1` to `s16`) to see exactly when the break fires:

   **Recovering `s16` — sends 0 A's:**

   The formula `blocksize - (byte_no % blocksize) - 1` with `byte_no = 15` gives `16 - 15 - 1 = 0`. So no attacker bytes are sent. The oracle encrypts just the secret:

   ```
   Block 1: [ s1  s2  s3  ...  s15  s16 ]   ← 0 A's; pure secret fills the block
   ```

   Lookup table: `[s1 s2 ... s15 ?]` for all 256 values. One matches → `s16` found. ✓

   **First probe after the secret is exhausted — byte_no = 16, sends 15 A's:**

   `16 - (16 % 16) - 1 = 15`. The oracle encrypts `15 A's || s1…s16` (31 bytes). PKCS#7 pads this to 32 bytes by appending `\x01`:

   ```
   Block 1: [ A  A  A  A  A  A  A  A  A  A  A  A  A  A  A  s1 ]
   Block 2: [ s2  s3  s4  ...  s16  \x01 ]   ← 15 known bytes + 1 padding byte
   ```

   Lookup table: `[s2 s3 ... s16 ?]` for all 256 values. When `? = \x01`, the table entry `AES-ECB([s2…s16 \x01])` matches Block 2 exactly → `\x01` is **falsely captured** as a secret byte and appended to `secret_msg`. The loop does not break here.

   **Second probe after exhaustion — byte_no = 17, sends 14 A's:**

   `16 - (17 % 16) - 1 = 14`. The oracle encrypts `14 A's || s1…s16` (30 bytes). PKCS#7 pads to 32 bytes with `\x02\x02`:

   ```
   Block 1: [ A  A  A  A  A  A  A  A  A  A  A  A  A  A  s1  s2 ]
   Block 2: [ s3  s4  ...  s16  \x02  \x02 ]   ← two padding bytes now occupy the block
   ```

   But the lookup table was built using `secret_msg`'s last 15 bytes, which now includes the falsely captured `\x01`. So crafted messages look like `[s2 … s16 \x01 ?]` — a completely different block content than `[s3 … s16 \x02 \x02]`. **No match is found → `target not in cipher_map` → break.** ✓

   > [!TIP]
   > Because exactly one padding byte (`\x01`) is falsely captured before the loop stops, `c4.py` strips it at the end with `secret_msg[blocksize-1:-1]` — the `[:-1]` discards that last garbage byte.

### Harder Case (with random prefix)
1. **Find `input_block_start`**: Compare ciphertexts for two different single-byte inputs; find the first differing block.
2. **Find prefix tail length `p`**: Increase input length until the input block stabilises (with false-positive guard).
3. **Compute total prefix length**: `prefix_length = input_block_start + p`
4. **Prepend `p` filler bytes**: Always add `p` filler bytes to your input to neutralise the prefix tail. Now proceed exactly as in the simple case, using `(input_block_start + p)` as the ciphertext offset for all lookups.

## My Implementation
- **Simple Case (no prefix):** [`c4.py`](../../../challenges/set2/c4.py)
- **Harder Case (with random prefix):** [`c6.py`](../../../challenges/set2/c6.py)

## Connected to
- [Modes of Operation (ECB)](../../concepts/ciphers/modes-of-operation.md)
- [Frequency Analysis](../../concepts/classical/frequency-analysis.md)
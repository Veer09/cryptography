# Advanced Encryption Standard (AES) — An In-Depth Technical Guide
## 1. Foundational Principles

Every secure cipher must satisfy two properties, first articulated by Claude Shannon in 1945:

| Property | Definition |
|---|---|
| **Confusion** | The relationship between the encryption key and the ciphertext must be as complex and mathematically opaque as possible, preventing an attacker from deducing the key even with large quantities of ciphertext. |
| **Diffusion** (Avalanche Effect) | The relationship between the plaintext and ciphertext must be highly intertwined. Flipping a single input bit should cause ~50% of output ciphertext bits to flip, destroying statistical patterns in the plaintext. |

Rather than achieving both properties in a single step — which is computationally impractical — modern ciphers build up confusion and diffusion incrementally through repeated **rounds**, each adding a small but provable amount of both properties.

---

## 2. Architecture Overview

**Cipher type:** Block cipher (operates on fixed-size data chunks)

### Block Size

| Consideration | Detail |
|---|---|
| Too small (e.g., 64-bit) | Vulnerable to the **Birthday Paradox**, enabling the [Sweet32 attack](https://sweet32.info/) |
| Too large | Cipher becomes prohibitively slow |
| **AES selection** | **128 bits (fixed)** |

### Key Size

The key must be large enough to resist brute-force attacks. Anything above 128 bits is currently computationally infeasible to brute-force. AES supports three key sizes:

| Variant | Key Size | Rounds |
|---|---|---|
| AES-128 | 128 bits | 10 |
| AES-192 | 192 bits | 12 |
| AES-256 | 256 bits | 14 |

### Macro Architecture: SPN vs. Feistel

Two general-purpose architectures exist for block ciphers:

**1. Feistel Network** (used in DES)
- Splits the block into two halves (Left, Right)
- Applies a keyed function to the Right half, then XORs the result with the Left half
- Swaps the halves and repeats
- *Advantage:* Decryption is structurally identical to encryption (keys applied in reverse)
- *Disadvantage:* Only half the block is processed per round — requires more rounds and is slower

**2. Substitution-Permutation Network (SPN)** ← *used by AES*
- Applies mathematical transformations to the **entire block** simultaneously each round
- Substitution adds **confusion**; Permutation adds **diffusion**
- *Advantage:* Faster full-block mixing per round
- *Disadvantage:* Requires a more explicit inverse for decryption

AES uses the **SPN architecture**.

---

## 3. The State Array

AES does not process a flat bit string. The 128-bit input block is broken into **16 bytes**, arranged into a **4×4 column-major matrix** called the **State Array**. Every AES operation reads and modifies this grid.

$$
\text{State} =
\begin{bmatrix}
a_{0,0} & a_{0,1} & a_{0,2} & a_{0,3} \\
a_{1,0} & a_{1,1} & a_{1,2} & a_{1,3} \\
a_{2,0} & a_{2,1} & a_{2,2} & a_{2,3} \\
a_{3,0} & a_{3,1} & a_{3,2} & a_{3,3}
\end{bmatrix}
$$

Similarly, the **key** is broken into bytes and arranged as a 4-row matrix, with the number of columns equal to `KeySize / 32`:

| Key Size | Columns |
|---|---|
| 128-bit | 4 |
| 192-bit | 6 |
| 256-bit | 8 |

This 2D layout makes diffusion more natural: spreading changes across both rows and columns ensures the Avalanche Effect propagates across the entire 128-bit state within just a few rounds.

---

## 4. Round Structure

Each round applies **four sequential layers** to the State:

| Layer | Operation | Purpose |
|---|---|---|
| 1 | SubBytes | Confusion |
| 2 | ShiftRows | Diffusion (horizontal) |
| 3 | MixColumns | Diffusion (vertical) |
| 4 | AddRoundKey | Key injection |

The **Final Round** omits MixColumns (explained in [Layer 3](#7-layer-3--mixcolumns-diffusion)).

All four operations are **invertible**, which is required for decryption.

---

## 5. Layer 1 — SubBytes (Confusion)

### What it does

SubBytes is a **non-linear byte substitution**. Every byte in the 4×4 State Array is independently replaced with a new byte via a fixed 256-entry lookup table called the **S-box**:

$$b_{i,j} = S(a_{i,j})$$

Since there are only 256 possible byte values, the transformation is precomputed into a static table to avoid redundant computation per encryption.

### Design requirements for the S-box

The substitution function $S$ must satisfy:

1. **Non-linearity** — If the substitution were a linear function (e.g., $y = ax + b$), an attacker could construct a system of linear equations and break the cipher via [Linear Cryptanalysis](http://cs.bc.edu/~straubin/crypto2017/heys.pdf).
2. **Invertibility** — A one-to-one (bijective) mapping must exist so decryption can recover the original byte. No two inputs may map to the same output.
3. **No fixed points** — There must be no byte $a$ such that $S(a) = a$ (and ideally no "opposite fixed points" where $S(a) = \bar{a}$).
4. **Resistance to Differential Cryptanalysis** — The probability that flipping specific input bits produces a predictable output difference must be minimized. See [Heys' tutorial](http://cs.bc.edu/~straubin/crypto2017/heys.pdf) for a detailed treatment.

### Why not a random table?

A randomly shuffled 256-entry table could, by chance, fail to meet the above criteria and provides no mathematical proof of resistance to linear or differential attacks.

### AES's chosen construction: $S(a) = g(f(a))$

The S-box is built from two composed functions:

**Step 1 — Multiplicative Inverse in $\mathrm{GF}(2^8)$ (adds non-linearity):**

$$f: a \mapsto b' = a^{-1} \pmod{p(x)}$$

where $p(x) = x^8 + x^4 + x^3 + x + 1$ is the AES irreducible polynomial. The byte `0x00` is mapped to itself (the multiplicative inverse of zero is undefined; this is a deliberate design choice). This operation achieves the **highest possible non-linearity** for an 8-bit function.

**Step 2 — Affine Transformation over $\mathrm{GF}(2)$ (adds algebraic complexity):**

$$g: b' \mapsto b = Ab' \oplus c$$

where $A$ is the following fixed $8 \times 8$ binary circulant matrix and $c = \texttt{0x63}$:

$$
A =
\begin{bmatrix}
1 & 0 & 0 & 0 & 1 & 1 & 1 & 1 \\
1 & 1 & 0 & 0 & 0 & 1 & 1 & 1 \\
1 & 1 & 1 & 0 & 0 & 0 & 1 & 1 \\
1 & 1 & 1 & 1 & 0 & 0 & 0 & 1 \\
1 & 1 & 1 & 1 & 1 & 0 & 0 & 0 \\
0 & 1 & 1 & 1 & 1 & 1 & 0 & 0 \\
0 & 0 & 1 & 1 & 1 & 1 & 1 & 0 \\
0 & 0 & 0 & 1 & 1 & 1 & 1 & 1 \\
\end{bmatrix},
\quad
c =
\begin{bmatrix} 0 \\ 1 \\ 1 \\ 0 \\ 0 \\ 0 \\ 1 \\ 1 \end{bmatrix}
$$

The affine transformation ensures:
- No fixed points or opposite fixed points remain
- The overall construction is algebraically complex enough to resist algebraic attacks (e.g., XSL attacks), even though the multiplicative inverse has a compact algebraic description

The Difference Distribution Table (DDT) of the S-box has a maximum entry of **4**, giving a maximum differential probability of $4/256 = 2^{-6}$ per round — this probability compounds multiplicatively across rounds, making differential attacks infeasible.

---

## 6. Layer 2 — ShiftRows (Diffusion)

### What it does

ShiftRows performs **horizontal byte permutation**. It cyclically shifts the rows of the State Array to the left by an offset equal to the row index:

$$
\begin{bmatrix}
a_{0,0} & a_{0,1} & a_{0,2} & a_{0,3} \\
a_{1,0} & a_{1,1} & a_{1,2} & a_{1,3} \\
a_{2,0} & a_{2,1} & a_{2,2} & a_{2,3} \\
a_{3,0} & a_{3,1} & a_{3,2} & a_{3,3}
\end{bmatrix}
\xrightarrow{}
\begin{bmatrix}
a_{0,0} & a_{0,1} & a_{0,2} & a_{0,3} \\
a_{1,1} & a_{1,2} & a_{1,3} & a_{1,0} \\
a_{2,2} & a_{2,3} & a_{2,0} & a_{2,1} \\
a_{3,3} & a_{3,0} & a_{3,1} & a_{3,2}
\end{bmatrix}
$$

| Row | Left shift |
|---|---|
| Row 0 | 0 bytes (unchanged) |
| Row 1 | 1 byte |
| Row 2 | 2 bytes |
| Row 3 | 3 bytes |

### Why it's necessary

SubBytes operates on individual bytes, and MixColumns mixes bytes only **within a single column** (vertically). Without ShiftRows, AES would be mathematically equivalent to **four independent 32-bit block ciphers** operating in parallel — each column isolated from the others.

ShiftRows breaks this column isolation. After the shift, bytes that originated in Column 0 now reside in Columns 0, 1, 2, and 3, guaranteeing that the next MixColumns step will mix information from all original columns. This is what causes the Avalanche Effect to propagate **across the full 128-bit block**.

---

## 7. Layer 3 — MixColumns (Diffusion)

### What it does

MixColumns performs **vertical mixing**. It takes each 4-byte column of the State and replaces it with a new 4-byte column, such that every output byte depends on all four input bytes in that column.

Each column vector $[s_{0,c},\ s_{1,c},\ s_{2,c},\ s_{3,c}]^T$ is multiplied by a fixed $4 \times 4$ matrix over $\mathrm{GF}(2^8)$:

$$
\begin{bmatrix} s'_{0,c} \\ s'_{1,c} \\ s'_{2,c} \\ s'_{3,c} \end{bmatrix}
= \begin{bmatrix}
02 & 03 & 01 & 01 \\
01 & 02 & 03 & 01 \\
01 & 01 & 02 & 03 \\
03 & 01 & 01 & 02
\end{bmatrix}
\begin{bmatrix} s_{0,c} \\ s_{1,c} \\ s_{2,c} \\ s_{3,c} \end{bmatrix}
$$


### Why this specific matrix: the MDS property

The chosen matrix is an **MDS (Maximum Distance Separable) matrix** with a **branch number of 5**. This means:

> If an attacker changes exactly **1 byte** of an input column, all **4 bytes** of the output column will change.

More formally, the branch number $\mathcal{B}$ is defined as:

$$\mathcal{B} = \min_{x \neq 0}\bigl(\text{wt}(x) + \text{wt}(Mx)\bigr) = 5$$

Combined with ShiftRows, this guarantees that after **2 rounds**, every output bit depends on every input bit — the full Avalanche Effect is achieved.

### Why MixColumns is omitted in the Final Round

MixColumns is a **purely linear operation**. Applying a linear transformation immediately before outputting the ciphertext provides zero additional cryptographic security, since a known-ciphertext attacker could simply invert the linear step. Removing it from the final round makes AES both faster and structurally symmetric between encryption and decryption, without any reduction in security.

---

## 8. Layer 4 — AddRoundKey (Key Mixing)

### What it does

AddRoundKey is the **only step where the secret key directly influences the data**. It performs a bitwise XOR between the 128-bit State and the current 128-bit Round Key:

$$S'_{i,j} = S_{i,j} \oplus K_{i,j}$$

### Why XOR?

XOR ($\oplus$) satisfies Shannon's requirement for key-dependent secrecy and has two critical properties:
1. **Speed** — XOR is a single CPU instruction, available in hardware on every modern processor
2. **Self-inverse** — $A \oplus K \oplus K = A$. To decrypt, you XOR with the same key; no separate inverse operation is needed

### Initial whitening

Before the first round, AES performs an initial `AddRoundKey` with the original master key (before any rounds execute). This is known as **key whitening** and ensures that even the very first round's SubBytes step operates on key-dependent data, preventing trivial analysis of the first round.

---

## 9. Key Expansion Schedule

AES requires one unique 128-bit Round Key per round, plus one for the initial whitening step. For AES-128, that is **11 Round Keys** total (10 rounds + 1 initial), derived from the single 128-bit master key.

The Key Expansion Schedule expands the master key into an array of 32-bit words $W_0, W_1, \ldots, W_{43}$ (for AES-128) using three operations:

| Operation | Description |
|---|---|
| **RotWord** | Cyclically shifts a 4-byte word: $[a_0, a_1, a_2, a_3] \to [a_1, a_2, a_3, a_0]$ |
| **SubWord** | Passes each byte of a word through the **same S-box** used in SubBytes |
| **Rcon** | XORs a round-dependent constant (derived from powers of 2 in $\mathrm{GF}(2^8)$) into the first word of each new round key |

**The role of Rcon** is critical: it introduces asymmetry between rounds, ensuring that a symmetric master key (e.g., all zeros or all identical bytes) does not produce symmetric or predictable round keys. It prevents **slide attacks** and eliminates key schedule symmetries.

**Security guarantee:** Even if an attacker recovers a round key (say, for Round 5), they cannot mathematically work backwards to reconstruct the original master key — the non-linear SubWord step (via the S-box) makes inversion computationally infeasible.

### Key expansion summary by variant

| Variant | Words generated | Round Keys produced |
|---|---|---|
| AES-128 | 44 ($W_0$–$W_{43}$) | 11 |
| AES-192 | 52 ($W_0$–$W_{51}$) | 13 |
| AES-256 | 60 ($W_0$–$W_{59}$) | 15 |

---

## 10. Round Count & Security Margin

As noted above, ShiftRows + MixColumns together guarantee **full diffusion by Round 2** — after just two rounds, every output bit depends on every input bit.

However, diffusion alone is not sufficient. Linear and differential cryptanalytic attacks have been theoretically demonstrated against reduced-round variants of AES:
- **6 rounds**: Vulnerable to certain differential distinguishers
- **7 rounds**: Best known attacks remain theoretical and far from practical

AES's round counts (10/12/14) were chosen to provide a comfortable security margin above the known cryptanalytic boundary, while remaining fast enough for hardware and software implementations.

| Variant | Rounds | Security margin above known attacks |
|---|---|---|
| AES-128 | 10 | ~3–4 rounds |
| AES-192 | 12 | ~5–6 rounds |
| AES-256 | 14 | ~7–8 rounds |

---
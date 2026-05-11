A **Galois Field** is a field with a finite number of elements. In these fields, arithmetic operations "wrap around" such that the result always stays within the defined finite set. 

A Galois Field is denoted as **$GF(q)$**, meaning it contains exactly $q$ elements.

---

## 1. The Rule of $q$
You cannot select any random integer for $q$. To satisfy the field axioms, a valid Galois Field must have an order that is a power of a prime:
$$q = p^n$$
- **$p$**: A prime number (called the **characteristic** of the field).
- **$n$**: A positive integer.

Based on the value of $n$, Galois Fields are categorized into two types:
1. **Prime Fields** ($n = 1$)
2. **Extension Fields** ($n > 1$)

---

## 2. Prime Fields: $GF(p)$
In a Prime Field, $n=1$, so $q=p$. The elements of $GF(p)$ are represented by the set of integers:
$$\{0, 1, \dots, p - 1\}$$

### Arithmetic Operations
Operations are performed using standard integer arithmetic followed by a modulo reduction:
1. **Addition:** $(a + b) \pmod p$
2. **Multiplication:** $(a \cdot b) \pmod p$

>  Why only Prime numbers?
> If $q$ were a composite number, the field would encounter the **Zero Divisor Problem**, preventing the existence of multiplicative inverses for all non-zero elements. (See [Zero Divisor Problem](algebraic-structure.md#difference-between-ring-and-field) for details).

---

## 3. Extension Fields: $GF(p^n)$
Since computers represent data in bits, we often require fields where $q = 2^n$. Because $2^n$ is composite for $n > 1$, we cannot use simple integer modulo arithmetic. Instead, we use **Polynomials** to represent elements and define new operations.

### Theoretical Construction: From Ring to Field
Formally, an extension field is constructed by starting with a polynomial ring and applying a modulo operation to turn it into a field.

1. **Polynomial Ring $F[x]$:** The set of all polynomials over a field $F$ (e.g., the prime field $GF(p)$) is denoted by $F[x]$.
   > **Why a Ring and not a Field?** In a Field, every non-zero element must have a multiplicative inverse. Most polynomials in $F[x]$ (like $x$) do not have an inverse that is also a polynomial (since $1/x$ is a fraction). Thus, $F[x]$ is only a Ring.

2. **Bounded Degree Polynomials $F[x]|_l$:** The set of polynomials over a field $F$, which have a degree strictly below $l$, is denoted by $F[x]|_l$. 

3. **Irreducible Polynomial $m(x)$:** An irreducible polynomial is one that cannot be factored into two non-trivial polynomials of lower degree in $F[x]$. Let $m(x)$ be an irreducible polynomial of degree $n$ over $F$.

4. **Quotient Ring $F[x] / \langle m(x) \rangle$ (The Field!):** To upgrade the Ring to a Field, we perform all polynomial arithmetic modulo the irreducible polynomial $m(x)$. 
   $$GF(p^n) \cong F[x] / \langle m(x) \rangle$$
   Just like prime numbers in integer fields, taking modulo $m(x)$ guarantees that every non-zero polynomial suddenly has a valid multiplicative inverse. This operation also naturally restricts all resulting polynomials to a degree less than $n$, meaning the elements of the Extension Field perfectly map to the set $F[x]|_n$.

### Practical Representation
An element in an Extension Field $GF(p^n)$ is practically represented as a polynomial $b(x)$ of degree less than $n$:
$$b(x) = b_{n-1}x^{n-1} + b_{n-2}x^{n-2} + \dots + b_1x + b_0$$
- **$b_i \in GF(p)$**: The coefficients belong to the underlying prime field.
- **$x$**: The **indeterminate**. It is an abstract placeholder and is never evaluated.

### Operations on Polynomials
To keep the field finite, we define two specific operations:

#### I. Addition
Summing polynomials consists of summing the coefficients with equal powers of $x$. The addition of coefficients occurs in the underlying field $GF(p)$:
$$c(x) = a(x) + b(x) \iff c_i = (a_i + b_i) \pmod p$$

#### II. Multiplication
Multiplication is performed in two steps:
   1. **Polynomial Multiplication:** Multiply $a(x)$ and $b(x)$ normally.
   2. **Modular Reduction:** To restrict the result back to the set $F[x]|_n$ (degree $< n$), we take the result modulo an **irreducible polynomial** $m(x)$.
   $$c(x) \equiv a(x) \cdot b(x) \pmod{m(x)}$$

---

## 4. Examples

### Example 1: Prime Field $GF(5)$
- **Set:** $\{0, 1, 2, 3, 4\}$
- **Addition:** $4 + 2 = 6 \equiv 1 \pmod 5$
- **Multiplication:** $3 \cdot 4 = 12 \equiv 2 \pmod 5$

### Example 2: Extension Field $GF(2^3)$
- **Elements:** Polynomials with coefficients from $GF(2)$ (0 or 1) and degree $< 3$ (the set $F[x]|_3$).
- **Irreducible Polynomial:** Let $m(x) = x^3 + x + 1$.
- **Multiplication:** $(x^2) \cdot (x) = x^3$.
- **Reduction:** $x^3 \pmod{x^3 + x + 1} = x + 1$.

---

## 5. Summary: Infinite vs. Finite Fields

| Property | Infinite Fields (Math) | Finite Fields (CS/Crypto) |
| :--- | :--- | :--- |
| **Examples** | $\mathbb{Q}, \mathbb{R}$ | $GF(p), GF(2^n)$ |
| **Memory** | Requires infinite precision | Fits in fixed registers (e.g. 8-bit) |
| **Overflow** | Numbers grow indefinitely | Results always "wrap around" |
| **Precision** | Floating point errors | Perfect integer precision |
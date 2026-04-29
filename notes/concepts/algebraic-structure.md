
**Galois Fields** (Finite Fields) are essential in cryptography. They are studied within **Abstract Algebra**, which focuses on algebraic structures rather than specific numbers.
> To define a Finite Field, we build upward through three structures:
> 1. **Groups** (One operation: Addition) 
> 2. **Rings** (Two operations: Addition & Multiplication)
> 3. **Fields** (Two operations + Multiplicative Inverses)

---

## 1. Groups
A **Group** is the most fundamental structure. It consists of a set $G$ and a single operation (conventionally denoted as $+$).

### The Operation
The operation $+$ is a mapping that combines two elements of $G$ to form a third element of $G$:
$$\text{+}: G \times G \to G \quad \text{where} \quad (a, b) \mapsto a + b$$

### Group Axioms
For $(G, +)$ to be a group, the operation must satisfy these four rules:

| Axiom | Formal Definition | Description |
| :--- | :--- | :--- |
| **Closure** | $\forall a, b \in G : a + b \in G$ | The result of the operation must stay within the set $G$. |
| **Associativity**| $\forall a, b, c \in G : (a + b) + c = a + (b + c)$ | The way elements are grouped does not change the result. |
| **Identity** | $\exists 0 \in G, \forall a \in G : a + 0 = a$ | There exists a "neutral" element $0$. |
| **Inverse** | $\forall a \in G, \exists b \in G : a + b = 0$ | Every element has an opposite that returns the identity. |

### Abelian Groups
If the group also satisfies the **Commutative** property, it is called an **Abelian Group**:
* **Commutativity:** $\forall a, b \in G : a + b = b + a$


> In this context, the symbol $+$ is an **abstract operator**. It does not necessarily represent standard arithmetic addition. In cryptographic applications (like AES), this operation is often implemented as a bitwise **XOR**.

---

## 2. Rings
A **Ring** is an extension of a group. While a group only has one operation, a Ring $(R, +, \cdot)$ incorporates two binary operations: **Addition ($+$)** and **Multiplication ($\cdot$)**.

### Ring Axioms
For a set $R$ to be a Ring, it must satisfy three primary conditions:

#### I. Additive Properties
The structure $(R, +)$ must be an **Abelian Group**. This means it satisfies all group axioms (Closure, Associativity, Identity, and Inverse) plus **Commutativity**.

#### II. Multiplicative Properties
The multiplication operation ($\cdot$) must satisfy:
* **Closure:** $\forall a, b \in R : a \cdot b \in R$
* **Associativity:** $\forall a, b, c \in R : (a \cdot b) \cdot c = a \cdot (b \cdot c)$
* **Multiplicative Identity:** $\exists 1 \in R, \forall a \in R : a \cdot 1 = a$ 
    *(Note: This $1$ is the neutral element for multiplication).*

#### III. Distributivity
Multiplication must distribute over addition, linking the two operations together:
> $$\forall a, b, c \in R : (a + b) \cdot c = (a \cdot c) + (b \cdot c)$$
> $$\forall a, b, c \in R : a \cdot (b + c) = (a \cdot b) + (a \cdot c)$$

### Commutative Rings
A ring is commutative if the multiplication operation also follows:
* **Commutativity:** $\forall a, b \in R : a \cdot b = b \cdot a$

---

## 3. Fields
A **Field** $(F, +, \cdot)$ is the most robust algebraic structure in this hierarchy. It is a Commutative Ring where every non-zero element has a multiplicative inverse. This allows for the operations of addition, subtraction, multiplication, and division.

### Field Axioms
For a set $F$ to be a Field, it must satisfy all the properties of a Commutative Ring, plus one critical requirement:

#### I. Multiplicative Inverse
For every element $a$ in $F$ (where $a \neq 0$), there exists an element $a^{-1}$ such that:
$$\forall a \in F \setminus \{0\}, \exists a^{-1} \in F : a \cdot a^{-1} = 1$$

The **Multiplicative Inverse** property is the defining boundary between a Ring and a Field. 

> In a Field, **division** is defined as multiplication by the multiplicative inverse:
> $$a \div b \equiv a \cdot b^{-1}$$
> Because a **Ring** does not guarantee the existence of $b^{-1}$ for all elements, division is not a universally defined operation within a Ring. In a **Field**, every non-zero element has an inverse, making division safe and consistent.

## Difference Between Ring and Field
### A Ring: $\mathbb{Z}_{6}$ (Integers modulo 6)
Consider the set $\{0, 1, 2, 3, 4, 5\}$ with addition and multiplication modulo 6.
- **Why it is a Ring:** It follows all additive group rules and multiplicative closure/associativity.
- **Why it is NOT a Field:** Look at the element $2$. 
    - Is there any number $x$ in the set such that $2 \cdot x \equiv 1 \pmod 6$? 
    - $2 \cdot 1 = 2$
    - $2 \cdot 2 = 4$
    - $2 \cdot 3 = 0$
    - $2 \cdot 4 = 2$
    - $2 \cdot 5 = 4$
- **Result:** $2$ has no multiplicative inverse in $\mathbb{Z}_{6}$. Therefore, you cannot "divide by 2" in this system.
- This is known as the **Zero Divisor** property. Elements that multiply to zero (like $2 \cdot 3 = 0 \pmod 6$) are zero divisors, and fields cannot contain them.

### A Field: $\mathbb{Z}_{5}$ (Integers modulo 5)
Consider the set $\{0, 1, 2, 3, 4\}$ with addition and multiplication modulo 5.
- **Why it is a Field:** Every non-zero element has a partner that multiplies to $1 \pmod 5$:
    - $1 \cdot 1 = 1$ (Inverse of $1$ is $1$)
    - $2 \cdot 3 = 6 \equiv 1$ (Inverse of $2$ is $3$)
    - $4 \cdot 4 = 16 \equiv 1$ (Inverse of $4$ is $4$)
- **Result:** Because every element $\{1, 2, 3, 4\}$ has an inverse, we can perform division. For example, $1 \div 2$ is the same as $1 \cdot 3 = 3$.
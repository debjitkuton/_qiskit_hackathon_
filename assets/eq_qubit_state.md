# Single-Qubit State & Normalization

## Visual Mathematical Formulation

$$|\psi\rangle = \alpha\,|0\rangle + \beta\,|1\rangle,\qquad |\alpha|^{2} + |\beta|^{2} = 1$$

## LaTeX Code

```latex
|\psi\rangle = \alpha\,|0\rangle + \beta\,|1\rangle,\qquad |\alpha|^{2} + |\beta|^{2} = 1
```

## Description & Context
Represents an arbitrary single-qubit quantum state as a coherent superposition of computational basis states $|0\rangle$ and $|1\rangle$, subject to the unitary normalization condition where the sum of measurement probabilities equals 1. Used in single-qubit channel qualification and state preparation.

## Qiskit Implementation

```python
from qiskit import QuantumCircuit
import numpy as np

# Prepare an arbitrary normalized single-qubit state
alpha = 1.0 / np.sqrt(2)
beta = 1.0 / np.sqrt(2)

qc = QuantumCircuit(1)
qc.initialize([alpha, beta], 0)
```

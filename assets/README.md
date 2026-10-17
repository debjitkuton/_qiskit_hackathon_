# Mathematical Equations & Metrics Catalog

This directory contains standalone mathematical formulations, generator scripts, and pre-rendered assets used throughout the **Quantum-Safe Secure Channel** project (Track PS-P1).

Each equation is documented in its own markdown file containing the LaTeX formulation, rendered visual asset, and Python Matplotlib generator source code.

---

## Catalog of Equations

| Equation | Document | LaTeX Formula | Asset |
| :--- | :--- | :--- | :--- |
| **Single-Qubit State** | [`eq_qubit_state.md`](eq_qubit_state.md) | $|\psi\rangle = \alpha\|0\rangle + \beta\|1\rangle,\; \|\alpha\|^2 + \|\beta\|^2 = 1$ | [`eq_qubit_state.png`](eq_qubit_state.png) |
| **Bell State $\lvert\Phi^+\rangle$** | [`eq_bell_state.md`](eq_bell_state.md) | $\|\Phi^{+}\rangle = \frac{1}{\sqrt{2}}(\|00\rangle + \|11\rangle)$ | [`eq_bell_state.png`](eq_bell_state.png) |
| **Parity Expectation $\langle ZZ \rangle$** | [`eq_zz_expectation.md`](eq_zz_expectation.md) | $\langle ZZ \rangle = \frac{N_{00} + N_{11} - N_{01} - N_{10}}{N}$ | [`eq_zz_expectation.png`](eq_zz_expectation.png) |
| **Bell State Fidelity** | [`eq_bell_fidelity.md`](eq_bell_fidelity.md) | $F = \langle \Phi^{+} \| \rho \| \Phi^{+} \rangle$ | [`eq_bell_fidelity.png`](eq_bell_fidelity.png) |
| **Standard Error** | [`eq_standard_error.md`](eq_standard_error.md) | $\mathrm{SE} = \frac{\sigma}{\sqrt{N}},\; \mathrm{SE}_{\langle ZZ\rangle} = \sqrt{\frac{1 - \langle ZZ \rangle^2}{N}}$ | [`eq_standard_error.png`](eq_standard_error.png) |
| **Coupling Graph Metrics** | [`eq_graph.md`](eq_graph.md) | $G=(V,E),\; \bar{d} = \frac{2}{n(n-1)}\sum_{i<j} d(i,j),\; \mathrm{diam}(G) = \max_{i,j} d(i,j)$ | [`eq_graph.png`](eq_graph.png) |

---

## Regenerating Assets

All equation images can be regenerated locally using Matplotlib:

```bash
python assets/eq_qubit_state.py
python assets/eq_bell_state.py
python assets/eq_zz_expectation.py
python assets/eq_bell_fidelity.py
python assets/eq_standard_error.py
python assets/eq_graph.py
```
